package com.csm.hybrids.entity;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModParticles;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
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
        GHOST_FLING("ghost_arm", "fling", 26, true);

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
                // it tears in out of nowhere
                Vec3 c = position().add(0, kind == Kind.FOX_PAW_SLAM ? 2.5 : 1.2, 0);
                for (int i = 0; i < 12; i++) {
                    level().addParticle(ModParticles.SMOKE.get(), c.x + random.nextGaussian() * 0.8,
                            c.y + random.nextGaussian() * 0.6, c.z + random.nextGaussian() * 0.8, 0, 0.02, 0);
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
