package com.csm.hybrids.ability;

import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.config.CsmConfig;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.BaseFireBlock;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * Shared helpers for moves. The user of a move is any {@link LivingEntity}: a hybrid player, or a devil mob using the
 * very same move against its target.
 */
public final class AbilityUtil {

    public static float dmg(float base) {
        return (float) (base * CsmConfig.DAMAGE_MULTIPLIER.get());
    }

    /** Damage of a move performed by {@code user}: devils fighting as mobs hit players less hard than players hit mobs. */
    public static float dmg(LivingEntity user, float base) {
        float d = dmg(base);
        if (user instanceof DevilEntity devil) {
            d *= devil.damageScale();
        }
        return d;
    }

    /**
     * The mod draws its own effects: status effects it hands out keep their HUD icon but never spray vanilla potion
     * swirls.
     */
    public static net.minecraft.world.effect.MobEffectInstance quiet(net.minecraft.world.effect.MobEffectInstance e) {
        return new net.minecraft.world.effect.MobEffectInstance(e.getEffect(), e.getDuration(), e.getAmplifier(),
                e.isAmbient(), false, e.showIcon());
    }

    public static boolean canHit(LivingEntity user, Entity e) {
        if (!(e instanceof LivingEntity living) || e == user || !living.isAlive() || e.isSpectator()
                || e instanceof ArmorStand || user.isAlliedTo(e)) {
            return false;
        }
        net.minecraft.nbt.CompoundTag tag = e.getPersistentData();
        if (tag.hasUUID(DevilEntity.THRALL_TAG) && tag.getUUID(DevilEntity.THRALL_TAG).equals(user.getUUID())) {
            return false; // your own thralls, dolls and what your snake let out
        }
        if (user instanceof Player player) {
            return !(e instanceof Player other) || player.canHarmPlayer(other);
        }
        if (e instanceof Player other && (other.isCreative() || other.isSpectator())) {
            return false;
        }
        if (user instanceof DevilEntity devil) {
            return devil.canHarm(living);
        }
        return true;
    }

    public static List<LivingEntity> inRadius(LivingEntity user, Vec3 center, double radius) {
        AABB box = new AABB(center, center).inflate(radius);
        return user.level().getEntitiesOfClass(LivingEntity.class, box,
                e -> canHit(user, e) && e.getBoundingBox().getCenter().distanceToSqr(center) <= radius * radius);
    }

    /** Living targets inside a view cone (angle measured from the look direction). */
    public static List<LivingEntity> inCone(LivingEntity user, double range, double halfAngleDeg) {
        return inCone(user, user.getEyePosition(), aim(user), range, halfAngleDeg);
    }

    public static List<LivingEntity> inCone(LivingEntity user, Vec3 eye, Vec3 look, double range, double halfAngleDeg) {
        double cos = Math.cos(Math.toRadians(halfAngleDeg));
        Vec3 dir = look.normalize();
        return user.level().getEntitiesOfClass(LivingEntity.class, new AABB(eye, eye).inflate(range + 2), e -> {
            if (!canHit(user, e)) {
                return false;
            }
            Vec3 to = e.getBoundingBox().getCenter().subtract(eye);
            double dist = to.length();
            if (dist > range + e.getBbWidth() * 0.5) {
                return false;
            }
            return dist < 1.2 + user.getBbWidth() * 0.5 || to.normalize().dot(dir) >= cos;
        });
    }

    /**
     * Where the user is aiming: a player's look vector; a mob aims at its target (or where it is looking when it has
     * none), since a mob's head rotation lags behind the fight.
     */
    public static Vec3 aim(LivingEntity user) {
        if (user instanceof Mob mob && !(user instanceof Player)) {
            LivingEntity t = mob.getTarget();
            if (t != null && t.isAlive()) {
                Vec3 d = t.getBoundingBox().getCenter().subtract(user.getEyePosition());
                if (d.lengthSqr() > 1e-4) {
                    return d.normalize();
                }
            }
            return user.getViewVector(1f);
        }
        return user.getLookAngle();
    }

    public static DamageSource source(LivingEntity user) {
        return user instanceof Player p ? user.damageSources().playerAttack(p) : user.damageSources().mobAttack(user);
    }

    public static boolean hurt(LivingEntity user, LivingEntity target, float amount) {
        return target.hurt(source(user), dmg(user, amount));
    }

    /** Re-hits a target that is still in its invulnerability frames (multi-hit sawing). */
    public static boolean hurtIgnoringIFrames(LivingEntity user, LivingEntity target, float amount) {
        target.invulnerableTime = 0;
        return hurt(user, target, amount);
    }

    public static void push(Entity target, Vec3 from, double strength, double up) {
        Vec3 d = target.position().subtract(from);
        Vec3 flat = new Vec3(d.x, 0, d.z);
        if (flat.lengthSqr() < 1e-4) {
            flat = new Vec3(0, 0, 1);
        }
        flat = flat.normalize().scale(strength);
        double resist = target instanceof LivingEntity l
                ? l.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.KNOCKBACK_RESISTANCE) : 0;
        double k = 1.0 - Mth.clamp(resist, 0, 1);
        target.setDeltaMovement(target.getDeltaMovement().add(flat.x * k, up * k, flat.z * k));
        target.hurtMarked = true;
    }

    public static void blood(ServerLevel level, Vec3 pos, int count, double spread) {
        Fx.blood(level, pos, count, spread);
        if (count >= 30) {
            Fx.gore(level, pos, count / 15);
        }
    }

    public static void sound(LivingEntity user, SoundEvent sound, float volume, float pitch) {
        user.level().playSound(null, user.getX(), user.getY() + user.getBbHeight() * 0.6, user.getZ(), sound,
                user instanceof Player ? SoundSource.PLAYERS : SoundSource.HOSTILE, volume, pitch);
    }

    public static void soundAt(ServerLevel level, Vec3 pos, SoundEvent sound, float volume, float pitch) {
        level.playSound(null, pos.x, pos.y, pos.z, sound, SoundSource.PLAYERS, volume, pitch);
    }

    public static ServerLevel level(LivingEntity user) {
        return (ServerLevel) user.level();
    }

    public static Vec3 right(LivingEntity user) {
        float yaw = (user instanceof Player ? user.getYRot() : user.yBodyRot) * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.cos(yaw), 0, -Mth.sin(yaw));
    }

    /** Rough world position of a hand/forearm tip, good enough to emit projectiles and particles. */
    public static Vec3 handPos(LivingEntity user, boolean rightHand, double forward) {
        Vec3 look = aim(user);
        Vec3 side = right(user).scale(rightHand ? 0.38 : -0.38);
        return user.getEyePosition().add(0, -0.42, 0).add(side).add(look.scale(forward));
    }

    /**
     * The target under the crosshair. Hitboxes are padded (more the further away they are) so long-range grabs
     * like Snare or Impale don't demand pixel-perfect aim. A mob just gets its own target when it is in range.
     */
    public static EntityHitResult raycastEntity(LivingEntity user, double range) {
        if (user instanceof Mob mob && !(user instanceof Player)) {
            LivingEntity t = mob.getTarget();
            if (t != null && t.isAlive() && t.distanceTo(user) <= range + t.getBbWidth() && mob.hasLineOfSight(t)) {
                return new EntityHitResult(t, t.getBoundingBox().getCenter());
            }
            return null;
        }
        Vec3 eye = user.getEyePosition();
        Vec3 end = eye.add(user.getLookAngle().scale(range));
        BlockHitResult block = user.level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user));
        Vec3 limit = block.getType() == BlockHitResult.Type.MISS ? end : block.getLocation();
        AABB box = user.getBoundingBox().expandTowards(limit.subtract(eye)).inflate(1.5);
        Entity best = null;
        Vec3 bestAt = null;
        double bestDist = Double.MAX_VALUE;
        for (Entity e : user.level().getEntities(user, box, e -> canHit(user, e))) {
            double pad = 0.25 + 0.03 * Math.sqrt(e.distanceToSqr(eye));
            AABB bb = e.getBoundingBox().inflate(pad);
            Vec3 at = bb.contains(eye) ? eye : bb.clip(eye, limit).orElse(null);
            if (at != null && eye.distanceToSqr(at) < bestDist) {
                best = e;
                bestAt = at;
                bestDist = eye.distanceToSqr(at);
            }
        }
        return best == null ? null : new EntityHitResult(best, bestAt);
    }

    /** Every target whose (padded) hitbox the segment from -> to passes through, nearest first. */
    public static List<LivingEntity> alongLine(LivingEntity user, Vec3 from, Vec3 to, double pad) {
        AABB box = new AABB(from, to).inflate(pad + 1.0);
        List<LivingEntity> out = new java.util.ArrayList<>(user.level().getEntitiesOfClass(LivingEntity.class, box,
                e -> canHit(user, e) && e.getBoundingBox().inflate(pad).clip(from, to).isPresent()));
        out.sort(java.util.Comparator.comparingDouble(e -> e.distanceToSqr(from)));
        return out;
    }

    /** Result of a hitscan shot: where it stopped and what it hit (null for a wall or nothing). */
    public record Shot(Vec3 end, @org.jetbrains.annotations.Nullable LivingEntity target) {
    }

    /** A bullet: stops at the first block or target along dir. */
    public static Shot shoot(LivingEntity user, Vec3 from, Vec3 dir, double range) {
        Vec3 end = from.add(dir.normalize().scale(range));
        BlockHitResult block = user.level().clip(new ClipContext(from, end, ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE, user));
        Vec3 limit = block.getType() == BlockHitResult.Type.MISS ? end : block.getLocation();
        List<LivingEntity> hits = alongLine(user, from, limit, 0.15);
        if (!hits.isEmpty()) {
            LivingEntity t = hits.get(0);
            Vec3 at = t.getBoundingBox().inflate(0.15).clip(from, limit).orElse(t.getBoundingBox().getCenter());
            return new Shot(at, t);
        }
        return new Shot(limit, null);
    }

    /** The first standing spot (feet position) at or just below p, or null over a drop. */
    public static Vec3 groundBelow(ServerLevel level, Vec3 p, int depth) {
        BlockPos pos = BlockPos.containing(p.x, p.y + 1.0, p.z);
        for (int i = 0; i < depth; i++) {
            BlockPos below = pos.below();
            if (!level.getBlockState(below).getCollisionShape(level, below).isEmpty()
                    && level.getBlockState(pos).getCollisionShape(level, pos).isEmpty()) {
                return new Vec3(p.x, pos.getY(), p.z);
            }
            pos = below;
        }
        return null;
    }

    public static BlockHitResult raycastBlock(LivingEntity user, double range) {
        Vec3 eye = user.getEyePosition();
        return user.level().clip(new ClipContext(eye, eye.add(aim(user).scale(range)),
                ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, user));
    }

    public static boolean griefing(ServerLevel level) {
        return CsmConfig.ABILITY_GRIEFING.get() && level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING);
    }

    public static void ignite(ServerLevel level, BlockPos pos) {
        if (!griefing(level)) {
            return;
        }
        if (level.isEmptyBlock(pos) && BaseFireBlock.canBePlacedAt(level, pos, net.minecraft.core.Direction.UP)) {
            level.setBlockAndUpdate(pos, BaseFireBlock.getState(level, pos));
        }
    }

    private AbilityUtil() {
    }
}
