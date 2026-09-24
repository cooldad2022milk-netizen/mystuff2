package com.csm.hybrids.entity;

import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.core.BlockPos;
import com.csm.hybrids.registry.ModParticles;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ItemSupplier;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** A glob of burning flamethrower fuel: explodes on impact and keeps the area burning. */
public class NapalmEntity extends Projectile implements ItemSupplier {
    private static final EntityDataAccessor<Boolean> BURNING = SynchedEntityData.defineId(NapalmEntity.class, EntityDataSerializers.BOOLEAN);
    private int burnTicks;
    private int life;

    public NapalmEntity(EntityType<? extends NapalmEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public NapalmEntity(Level level, LivingEntity owner) {
        this(ModEntities.NAPALM.get(), level);
        setOwner(owner);
    }

    @Override
    protected void defineSynchedData() {
        this.entityData.define(BURNING, false);
    }

    public boolean isBurning() {
        return this.entityData.get(BURNING);
    }

    @Override
    public void tick() {
        super.tick();
        if (isBurning()) {
            setDeltaMovement(Vec3.ZERO);
            if (level().isClientSide) {
                for (int i = 0; i < 4; i++) {
                    double a = random.nextDouble() * Math.PI * 2;
                    double r = random.nextDouble() * 2.6;
                    level().addParticle(i == 0 ? ModParticles.SMOKE.get() : (i == 1 ? ModParticles.EMBER.get() : ModParticles.FIRE.get()),
                            getX() + Math.cos(a) * r, getY() + 0.1, getZ() + Math.sin(a) * r, 0, 0.06 + random.nextDouble() * 0.05, 0);
                }
            } else {
                if (++burnTicks % 10 == 0) {
                    for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(blockPosition()).inflate(3.2))) {
                        if (getOwner() instanceof ServerPlayer sp && !AbilityUtil.canHit(sp, e)) {
                            continue;
                        }
                        e.setSecondsOnFire(5);
                        e.hurt(damageSources().mobProjectile(this, getOwner() instanceof LivingEntity l ? l : null), AbilityUtil.dmg(2f));
                    }
                }
                if (burnTicks > 80) {
                    discard();
                }
            }
            return;
        }
        if (!level().isClientSide) {
            HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
            if (hit.getType() != HitResult.Type.MISS) {
                Vec3 at = hit.getLocation();
                setPos(at.x, at.y, at.z);
                ignite((ServerLevel) level());
                return;
            }
            if (++life > 100) {
                discard();
                return;
            }
        } else {
            level().addParticle(ModParticles.FIRE.get(), getX(), getY(), getZ(), 0, 0.01, 0);
            level().addParticle(ModParticles.FIRE.get(), getX(), getY(), getZ(), random.nextGaussian() * 0.03, 0.03,
                    random.nextGaussian() * 0.03);
            if (tickCount % 2 == 0) {
                level().addParticle(ModParticles.SMOKE.get(), getX(), getY(), getZ(), 0, 0.02, 0);
            }
        }
        Vec3 v = getDeltaMovement();
        setPos(getX() + v.x, getY() + v.y, getZ() + v.z);
        setDeltaMovement(v.x * 0.99, v.y - 0.035, v.z * 0.99);
        updateRotation();
    }

    private void ignite(ServerLevel level) {
        Entity owner = getOwner();
        boolean fire = AbilityUtil.griefing(level);
        // our own blast instead of a vanilla explosion (no vanilla particles, no block damage)
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(blockPosition()).inflate(3.0))) {
            if (owner instanceof ServerPlayer sp && !AbilityUtil.canHit(sp, e)) {
                continue;
            }
            e.hurt(damageSources().mobProjectile(this, owner instanceof LivingEntity l ? l : null), AbilityUtil.dmg(9f));
            AbilityUtil.push(e, position(), 0.9, 0.4);
        }
        Vec3 c = position();
        Fx.fireBurst(level, c.add(0, 0.2, 0), 40, 0.3);
        Fx.fireJet(level, c, new Vec3(0, 1, 0), 24, 0.35, 0.5);
        Fx.smoke(level, c.add(0, 0.8, 0), 12, 1.0);
        Fx.embers(level, c, 20, 0.8);
        Fx.shockwave(level, c, 4.0, Fx.FIRE_RING);
        Fx.impact(level, c.add(0, 0.6, 0), 2.2);
        level.playSound(null, getX(), getY(), getZ(), ModSounds.FLAME_BURST.get(), SoundSource.PLAYERS, 1.2f, 0.9f);
        if (fire) {
            for (int i = 0; i < 10; i++) {
                BlockPos p = BlockPos.containing(getX() + random.nextGaussian() * 1.6, getY() + 0.5, getZ() + random.nextGaussian() * 1.6);
                for (int dy = 1; dy >= -2; dy--) {
                    BlockPos q = p.above(dy);
                    if (level.isEmptyBlock(q) && !level.isEmptyBlock(q.below())) {
                        AbilityUtil.ignite(level, q);
                        break;
                    }
                }
            }
        }
        if (owner instanceof ServerPlayer sp) {
            for (LivingEntity e : AbilityUtil.inRadius(sp, position(), 3.5)) {
                e.setSecondsOnFire(8);
            }
        }
        this.entityData.set(BURNING, true);
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && entity != getOwner();
    }

    @Override
    public ItemStack getItem() {
        return new ItemStack(Items.FIRE_CHARGE);
    }

    @Override
    public boolean isOnFire() {
        return false;
    }
}
