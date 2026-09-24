package com.csm.hybrids.entity;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.contract.Contracts;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModParticles;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * The part of a contract devil its contractor calls up: only ever that part, for as long as the attack lasts, then
 * it is gone again.
 * <ul>
 *   <li>{@link Kind#FOX_HEAD} - "Kon!": the Fox Devil's head (and nothing else) appears around the prey and bites.</li>
 *   <li>{@link Kind#FOX_PAW_SLAM} / {@link Kind#FOX_PAW_SWIPE} - the Fox Devil's eyed paw, for contractors it doesn't
 *       find handsome enough to lend its head to.</li>
 *   <li>{@link Kind#CURSE} - after the third nail the Curse Devil stands up behind its victim, seizes it by the arms
 *       and bites into its neck and shoulders.</li>
 *   <li>{@link Kind#GHOST_HAND} / {@link Kind#GHOST_FLING} - the Ghost Devil's right arm. Only its contractor can see
 *       it (others see a faint shimmer).</li>
 *   <li>{@link Kind#SNAKE_SWALLOW} / {@link Kind#SNAKE_RELEASE} - the Snake Devil's head out of the ground: it swallows
 *       its prey whole, or spits out something it swallowed earlier. {@link Kind#SNAKE_TAIL} - its tail.</li>
 *   <li>{@link Kind#OCTOPUS_GRAB} - the Octopus Devil's tentacles out of ink clouds; {@link Kind#OCTOPUS_LIFT} - one
 *       tentacle under the contractor's feet, flinging them.</li>
 * </ul>
 * The server runs what the part does (its bite, grip, slam) here, so it keeps working after the contractor's own move
 * has finished. Positions are set once when summoned (the ghost's grip rises as it lifts its prey).
 */
public class ContractSummonEntity extends Entity implements GeoEntity {
    private static final EntityDataAccessor<Integer> KIND = SynchedEntityData.defineId(ContractSummonEntity.class,
            EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> OWNER = SynchedEntityData.defineId(ContractSummonEntity.class,
            EntityDataSerializers.INT);

    public enum Kind {
        FOX_HEAD("fox_head", "kon", 24, false),
        FOX_PAW_SLAM("fox_paw", "slam", 26, false),
        FOX_PAW_SWIPE("fox_paw", "swipe", 22, false),
        CURSE("curse", "seize", 64, false),
        GHOST_HAND("ghost_arm", "strangle", 54, true),
        GHOST_FLING("ghost_arm", "fling", 26, true),
        SNAKE_SWALLOW("snake_head", "swallow", 36, false),
        SNAKE_RELEASE("snake_head", "release", 34, false),
        SNAKE_TAIL("snake_tail", "tail", 26, false),
        OCTOPUS_GRAB("octopus", "grab", 52, false),
        OCTOPUS_LIFT("octopus", "lift", 22, false);

        /** geo/entity/contract/&lt;model&gt;.geo.json (and the texture and animation file of the same name). */
        public final String model;
        public final String anim;
        public final int life;
        /** Drawn see-through; only the contractor sees it clearly. */
        public final boolean ghostly;
        final RawAnimation raw;

        Kind(String model, String anim, int life, boolean ghostly) {
            this.model = model;
            this.anim = anim;
            this.life = life;
            this.ghostly = ghostly;
            this.raw = RawAnimation.begin().thenPlayAndHold(anim);
        }
    }

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    /** Server only: whoever called it (the damage is theirs) and what it came for. */
    @Nullable
    private LivingEntity owner;
    @Nullable
    private LivingEntity victim;
    private Vec3 anchor = Vec3.ZERO;
    /** Everything else the tentacles took hold of. */
    private final java.util.List<LivingEntity> held = new java.util.ArrayList<>();

    public ContractSummonEntity(EntityType<? extends ContractSummonEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    /**
     * Calls the part up at {@code pos}, turned to face {@code facing} (the direction its front - the fox's snout, the
     * Curse's chest, the ghost's grip - points).
     */
    public static ContractSummonEntity summon(ServerLevel level, Kind kind, LivingEntity owner,
                                              @Nullable LivingEntity victim, Vec3 pos, Vec3 facing) {
        ContractSummonEntity e = new ContractSummonEntity(ModEntities.CONTRACT_SUMMON.get(), level);
        e.entityData.set(KIND, kind.ordinal());
        e.entityData.set(OWNER, owner.getId());
        e.owner = owner;
        e.victim = victim;
        e.anchor = pos;
        float yaw = facing.horizontalDistanceSqr() > 1e-6
                ? (float) (Mth.atan2(facing.z, facing.x) * Mth.RAD_TO_DEG) - 90f : owner.getYRot();
        e.moveTo(pos.x, pos.y, pos.z, yaw, 0f);
        e.yRotO = yaw;
        level.addFreshEntity(e);
        return e;
    }

    public Kind kind() {
        int i = entityData.get(KIND);
        Kind[] all = Kind.values();
        return i >= 0 && i < all.length ? all[i] : Kind.FOX_HEAD;
    }

    /** Entity id of the contractor (clients use it to decide who can see a ghost's arm). */
    public int ownerId() {
        return entityData.get(OWNER);
    }

    /** The way the part faces, from its yaw. */
    public Vec3 facing() {
        float yaw = getYRot() * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(yaw), 0, Mth.cos(yaw));
    }

    @Override
    protected void defineSynchedData() {
        entityData.define(KIND, 0);
        entityData.define(OWNER, -1);
    }

    @Override
    public void tick() {
        super.tick();
        Kind kind = kind();
        if (level().isClientSide) {
            if (tickCount == 1 && !kind.ghostly) {
                // it tears in out of nowhere (the octopus's tentacles come out of ink, the snake out of the ground)
                boolean ink = kind == Kind.OCTOPUS_GRAB || kind == Kind.OCTOPUS_LIFT;
                boolean ground = kind == Kind.SNAKE_SWALLOW || kind == Kind.SNAKE_RELEASE || kind == Kind.SNAKE_TAIL;
                Vec3 c = position().add(0, kind == Kind.FOX_PAW_SLAM ? 2.5 : ground || ink ? 0.3 : 1.2, 0);
                for (int i = 0; i < (ink ? 30 : 12); i++) {
                    level().addParticle(ink ? ModParticles.INK.get() : ground ? ModParticles.CLOD.get() : ModParticles.SMOKE.get(),
                            c.x + random.nextGaussian() * (ink ? 1.4 : 0.8), c.y + random.nextGaussian() * 0.4,
                            c.z + random.nextGaussian() * (ink ? 1.4 : 0.8), 0, ground ? 0.25 : 0.02, 0);
                }
            }
            return;
        }
        if (owner == null || !owner.isAlive() || tickCount > kind.life) {
            if (tickCount > kind.life - 2 && !kind.ghostly) {
                Fx.smoke((ServerLevel) level(), position().add(0, 1, 0), 10, 0.8);
            }
            discard();
            return;
        }
        ServerLevel level = (ServerLevel) level();
        switch (kind) {
            case FOX_HEAD -> foxHead(level, owner);
            case FOX_PAW_SLAM -> pawSlam(level, owner);
            case FOX_PAW_SWIPE -> pawSwipe(level, owner);
            case CURSE -> curse(level, owner);
            case GHOST_HAND -> ghostHand(level, owner);
            case GHOST_FLING -> ghostFling(level, owner);
            case SNAKE_SWALLOW -> snakeSwallow(level, owner);
            case SNAKE_RELEASE -> snakeRelease(level, owner);
            case SNAKE_TAIL -> snakeTail(level, owner);
            case OCTOPUS_GRAB -> octopusGrab(level, owner);
            case OCTOPUS_LIFT -> {
                if (tickCount % 4 == 0) {
                    Fx.ink(level, anchor.add(0, 0.2, 0), 4, 0.6);
                }
            }
        }
    }

    @Nullable
    private LivingEntity victim() {
        return victim != null && victim.isAlive() ? victim : null;
    }

    /** Holds {@code e} hanging at {@code at} (feet position). */
    private static void hold(LivingEntity e, Vec3 at) {
        e.setDeltaMovement(at.subtract(e.position()).scale(0.4));
        e.fallDistance = 0;
        e.hurtMarked = true;
    }

    private static boolean small(LivingEntity e) {
        return !(e instanceof Player) && e.getMaxHealth() <= 100f
                && !(e instanceof DevilEntity d && d.spec().boss);
    }

    // ================================================================== Fox Devil
    /** The head lunges out of nothing with its jaws wide and snaps them shut on whatever is between them. */
    private void foxHead(ServerLevel level, LivingEntity owner) {
        if (tickCount == 3) {
            AbilityUtil.soundAt(level, position(), ModSounds.DEVIL_GROWL.get(), 1.5f, 1.25f);
        }
        if (tickCount != 9) {
            return;
        }
        Vec3 jaws = position().add(0, 1.0, 0);
        AbilityUtil.soundAt(level, jaws, ModSounds.DEVIL_BITE.get(), 2.0f, 0.75f);
        for (LivingEntity e : AbilityUtil.inRadius(owner, jaws, 2.6)) {
            AbilityUtil.hurtIgnoringIFrames(owner, e, 24f);
            Vec3 c = e.getBoundingBox().getCenter();
            // it swallows small prey whole or tears it apart
            if (e.isAlive() && small(e) && e.getHealth() < e.getMaxHealth() * 0.3f) {
                AbilityUtil.hurtIgnoringIFrames(owner, e, 1000f);
            }
            AbilityUtil.blood(level, c, 60, 0.45);
            Fx.bloodSpray(level, c, facing(), 20, 0.5);
            Fx.gore(level, c, 3);
        }
    }

    /** The paw comes down on the prey out of the sky, claws first. */
    private void pawSlam(ServerLevel level, LivingEntity owner) {
        if (tickCount != 8) {
            return;
        }
        Vec3 p = position();
        AbilityUtil.soundAt(level, p, ModSounds.DEVIL_SLAM.get(), 2.0f, 0.8f);
        Fx.shockwave(level, p, 3.6, Fx.BLOOD_RING);
        Fx.clods(level, p, 26, 0.5);
        for (LivingEntity e : AbilityUtil.inRadius(owner, p.add(0, 0.6, 0), 2.8)) {
            AbilityUtil.hurtIgnoringIFrames(owner, e, 16f);
            e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 50, 3)));
            e.setDeltaMovement(e.getDeltaMovement().multiply(0.2, 0, 0.2).add(0, -0.6, 0));
            e.hurtMarked = true;
            AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 36, 0.4);
        }
    }

    /** The paw sweeps across in front of the contractor and bats everything aside. */
    private void pawSwipe(ServerLevel level, LivingEntity owner) {
        if (tickCount != 8) {
            return;
        }
        Vec3 fwd = facing();
        Vec3 side = new Vec3(fwd.z, 0, -fwd.x); // the paw sweeps from the contractor's right to the left
        Vec3 eye = owner.getEyePosition();
        AbilityUtil.soundAt(level, eye, ModSounds.DEVIL_GUST.get(), 1.6f, 0.9f);
        Fx.slash(level, eye.add(fwd.scale(3.0)), side.add(0, -0.3, 0), 3.4);
        for (LivingEntity e : AbilityUtil.inCone(owner, eye, fwd, 6.5, 75)) {
            AbilityUtil.hurtIgnoringIFrames(owner, e, 12f);
            Vec3 fling = side.scale(1.4).add(fwd.scale(0.6));
            e.setDeltaMovement(fling.x, 0.55, fling.z);
            e.hurtMarked = true;
            AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 24, 0.3);
        }
    }

    // ================================================================== Curse Devil
    /**
     * It stands up out of the ground behind its victim, takes it by both arms (a crucifixion) and bites into its
     * neck and shoulders until the third bite finishes it.
     */
    private void curse(ServerLevel level, LivingEntity owner) {
        if (tickCount == 2) {
            AbilityUtil.soundAt(level, position(), ModSounds.DEVIL_ROAR.get(), 2.0f, 0.5f);
            Fx.clods(level, position(), 30, 0.45);
        }
        LivingEntity v = victim();
        if (v == null || tickCount < 10 || tickCount > 50) {
            return;
        }
        Vec3 grip = anchor.add(facing().scale(1.3)).add(0, 2.2, 0);
        hold(v, grip);
        v.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 10, 5)));
        if (tickCount == 14) {
            AbilityUtil.soundAt(level, grip, ModSounds.CONTROL_CRUSH.get(), 1.6f, 0.6f);
        }
        if (tickCount == 22 || tickCount == 32) {
            AbilityUtil.hurtIgnoringIFrames(owner, v, 8f);
            AbilityUtil.soundAt(level, grip, ModSounds.DEVIL_BITE.get(), 1.8f, 0.6f);
            AbilityUtil.blood(level, v.getEyePosition(), 40, 0.35);
        }
        if (tickCount == 44) {
            float dmg = Math.max(40f, v.getMaxHealth() * 0.35f);
            AbilityUtil.hurtIgnoringIFrames(owner, v, dmg);
            AbilityUtil.soundAt(level, grip, ModSounds.CONTROL_CRUSH.get(), 2.0f, 0.5f);
            Vec3 c = v.getBoundingBox().getCenter();
            AbilityUtil.blood(level, c, 120, 0.6);
            Fx.gore(level, c, 6);
            Fx.impact(level, c, 2.4);
            v.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 3)));
            v.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 200, 1)));
        }
    }

    // ================================================================== Ghost Devil
    /** The invisible hand closes round the prey's throat and lifts it off the ground. */
    private void ghostHand(ServerLevel level, LivingEntity owner) {
        LivingEntity v = victim();
        double lift = Math.min(1.4, Math.max(0, tickCount - 6) * 0.15);
        setPos(anchor.x, anchor.y + lift, anchor.z);
        if (v == null || tickCount < 4 || tickCount > 48) {
            return;
        }
        if (tickCount == 4) {
            AbilityUtil.soundAt(level, v.getEyePosition(), ModSounds.CONTROL_CRUSH.get(), 0.9f, 1.5f);
        }
        hold(v, position().subtract(0, v.getBbHeight() * 0.85, 0));
        v.setAirSupply(Math.max(-10, v.getAirSupply() - 20));
        v.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 10, 4)));
        if (tickCount % 8 == 0) {
            AbilityUtil.hurtIgnoringIFrames(owner, v, 4f);
            Fx.smoke(level, v.getEyePosition(), 3, 0.2);
        }
    }

    /** The invisible hand snatches the prey up and hurls it aside. */
    private void ghostFling(ServerLevel level, LivingEntity owner) {
        LivingEntity v = victim();
        if (v == null || tickCount < 3 || tickCount > 12) {
            return;
        }
        if (tickCount < 12) {
            hold(v, anchor.add(0, Math.min(1.2, (tickCount - 3) * 0.2), 0));
            return;
        }
        Vec3 fwd = facing();
        Vec3 side = new Vec3(fwd.z, 0, -fwd.x).scale(random.nextBoolean() ? 1 : -1);
        Vec3 fling = side.add(fwd.scale(0.5)).normalize().scale(1.7);
        v.setDeltaMovement(fling.x, 0.9, fling.z);
        v.hurtMarked = true;
        AbilityUtil.hurtIgnoringIFrames(owner, v, 10f);
        AbilityUtil.soundAt(level, v.position(), ModSounds.DEVIL_GUST.get(), 1.2f, 1.4f);
    }

    // ================================================================== Snake Devil
    /** It rears behind the prey and strikes down: its jaws (a mouth of interlocking hands) close round it on tick 11. */
    private void snakeSwallow(ServerLevel level, LivingEntity owner) {
        if (tickCount == 2) {
            AbilityUtil.soundAt(level, position(), ModSounds.DEVIL_ROAR.get(), 1.6f, 1.3f);
            Fx.clods(level, position(), 30, 0.5);
            Fx.shockwave(level, position(), 3.0, Fx.STEEL_RING);
        }
        LivingEntity v = victim();
        if (v != null && tickCount > 3 && tickCount < 11 && v.distanceToSqr(anchor) < 9) {
            hold(v, anchor); // it can't get out from under the strike
        }
        if (tickCount != 11) {
            return;
        }
        Vec3 jaws = anchor.add(0, 1.2, 0);
        AbilityUtil.soundAt(level, jaws, ModSounds.DEVIL_BITE.get(), 2.0f, 0.6f);
        for (LivingEntity e : AbilityUtil.inRadius(owner, jaws, 2.8)) {
            Vec3 c = e.getBoundingBox().getCenter();
            boolean weak = e.getHealth() <= e.getMaxHealth() * 0.5f || e.getMaxHealth() <= 30f;
            if ((e == v || v == null) && weak && owner instanceof ServerPlayer sp && Contracts.swallow(sp, e)) {
                v = null; // gone down whole
                AbilityUtil.soundAt(level, jaws, ModSounds.BLOOD_DRINK.get(), 1.6f, 0.5f);
                Fx.smoke(level, jaws, 6, 0.4);
                sp.displayClientMessage(Component.translatable("msg.csm.snake_swallowed", e.getDisplayName(),
                        Contracts.bellyCount(sp), Contracts.BELLY_SIZE).withStyle(ChatFormatting.DARK_GREEN), true);
                continue;
            }
            AbilityUtil.hurtIgnoringIFrames(owner, e, e == victim ? 20f : 10f);
            AbilityUtil.blood(level, c, 50, 0.45);
            Fx.gore(level, c, 2);
        }
    }

    /** It rises, opens its mouth and lets out the last thing it swallowed, whole and healed, to fight for you. */
    private void snakeRelease(ServerLevel level, LivingEntity owner) {
        if (tickCount == 2) {
            AbilityUtil.soundAt(level, position(), ModSounds.DEVIL_ROAR.get(), 1.4f, 1.2f);
            Fx.clods(level, position(), 24, 0.45);
        }
        if (tickCount != 14 || !(owner instanceof ServerPlayer sp)) {
            return;
        }
        Vec3 mouth = anchor.add(facing().scale(1.7)).add(0, 1.4, 0);
        LivingEntity out = Contracts.release(sp, mouth, getYRot() + 180f);
        AbilityUtil.soundAt(level, mouth, ModSounds.DEVIL_GROWL.get(), 1.6f, 0.7f);
        Fx.smoke(level, mouth, 10, 0.5);
        AbilityUtil.blood(level, mouth, 20, 0.4);
        if (out != null) {
            if (victim() != null && out instanceof net.minecraft.world.entity.Mob m) {
                m.setTarget(victim());
                sp.setLastHurtMob(victim());
            }
            sp.displayClientMessage(Component.translatable("msg.csm.snake_released", out.getDisplayName())
                    .withStyle(ChatFormatting.DARK_GREEN), true);
        }
    }

    /** The tail comes up beside the contractor and swats across everything in front of them. */
    private void snakeTail(ServerLevel level, LivingEntity owner) {
        if (tickCount == 2) {
            Fx.clods(level, position(), 20, 0.4);
        }
        if (tickCount != 10) {
            return;
        }
        Vec3 fwd = facing();
        Vec3 side = new Vec3(fwd.z, 0, -fwd.x); // from the contractor's right to their left
        Vec3 eye = owner.getEyePosition();
        AbilityUtil.soundAt(level, eye, ModSounds.DEVIL_GUST.get(), 1.8f, 0.7f);
        Fx.slash(level, eye.add(fwd.scale(3.0)).add(0, -0.6, 0), side, 3.6);
        for (LivingEntity e : AbilityUtil.inCone(owner, eye, fwd, 7.5, 80)) {
            AbilityUtil.hurtIgnoringIFrames(owner, e, 13f);
            Vec3 fling = side.scale(1.6).add(fwd.scale(0.5));
            e.setDeltaMovement(fling.x, 0.6, fling.z);
            e.hurtMarked = true;
            AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 20, 0.3);
        }
    }

    // ================================================================== Octopus Devil
    /** Tentacles out of the ink coil round the target (and up to three others near it), lift, squeeze and slam. */
    private void octopusGrab(ServerLevel level, LivingEntity owner) {
        if (tickCount % 5 == 1 && tickCount < 44) {
            Fx.ink(level, anchor.add(0, 0.3, 0), 6, 1.4);
        }
        if (tickCount == 6) {
            AbilityUtil.soundAt(level, anchor, ModSounds.WHIP_LASH.get(), 1.4f, 0.5f);
            LivingEntity v = victim();
            if (v != null && v.distanceToSqr(anchor) < 16) {
                held.add(v);
            }
            for (LivingEntity e : AbilityUtil.inRadius(owner, anchor.add(0, 1, 0), 4.5)) {
                if (held.size() >= 4) {
                    break;
                }
                if (!held.contains(e)) {
                    held.add(e);
                }
            }
        }
        if (tickCount < 6 || tickCount > 40) {
            return;
        }
        held.removeIf(e -> !e.isAlive());
        for (int i = 0; i < held.size(); i++) {
            LivingEntity e = held.get(i);
            double a = i == 0 ? 0 : (i - 1) * 2.1;
            Vec3 ring = i == 0 ? Vec3.ZERO : new Vec3(Math.cos(a) * 1.8, 0, Math.sin(a) * 1.8);
            double lift = Math.min(2.4, (tickCount - 6) * 0.18);
            if (tickCount < 38) {
                hold(e, anchor.add(ring).add(0, lift, 0));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 10, 5)));
            }
            if (tickCount % 8 == 6) {
                AbilityUtil.hurtIgnoringIFrames(owner, e, 3f);
                Fx.ink(level, e.getBoundingBox().getCenter(), 2, 0.3);
            }
            if (tickCount == 38) {
                e.setDeltaMovement(0, -1.6, 0);
                e.hurtMarked = true;
            }
            if (tickCount == 40) {
                AbilityUtil.hurtIgnoringIFrames(owner, e, 12f);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 36, 0.4);
                Fx.clods(level, e.position(), 16, 0.4);
            }
        }
        if (tickCount == 40) {
            AbilityUtil.soundAt(level, anchor, ModSounds.DEVIL_SLAM.get(), 1.8f, 0.8f);
            Fx.shockwave(level, anchor, 3.8, Fx.STEEL_RING);
        }
    }

    // ================================================================== plumbing
    @Override
    public boolean shouldBeSaved() {
        return false; // it only exists for the length of one attack
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return new ClientboundAddEntityPacket(this);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 0, state -> state.setAndContinue(kind().raw)));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
