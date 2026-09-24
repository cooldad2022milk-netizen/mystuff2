package com.csm.hybrids.entity.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.devil.DevilAbility;
import com.csm.hybrids.devil.DevilSpec;
import com.csm.hybrids.devil.DevilSpecs;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModEntities;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomFlyingGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.function.Predicate;

/**
 * A full devil fought as a mob. One class serves every devil: stats come from its {@link DevilSpec}, its moves are
 * the very {@link DevilAbility} objects a player who became that devil uses from the ability wheel, run by
 * {@link DevilMoveGoal}. Devils with extra rules (Makima's contract, the Darkness Devil's fear of light, the Tomato
 * Devil's seeds...) subclass this.
 * <p>
 * The same class also serves as a client-only "puppet": the devil model drawn in place of a player in devil form.
 */
public class DevilEntity extends Monster implements GeoEntity {
    private static final EntityDataAccessor<String> FX = SynchedEntityData.defineId(DevilEntity.class,
            EntityDataSerializers.STRING);
    private static final EntityDataAccessor<Integer> FX_END = SynchedEntityData.defineId(DevilEntity.class,
            EntityDataSerializers.INT);
    public static final String THRALL_TAG = "csm_thrall_of";

    protected static final RawAnimation IDLE = RawAnimation.begin().thenLoop("idle");
    protected static final RawAnimation MOVE = RawAnimation.begin().thenLoop("move");
    protected static final RawAnimation DEATH = RawAnimation.begin().thenPlayAndHold("death");

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    @Nullable
    private final ServerBossEvent bossEvent;
    /** Server: the move being performed. */
    @Nullable
    public AbilityRun activeRun;

    /** Client puppets only: the player wearing this form, and where their effect groups come from. */
    @Nullable
    public Player owner;
    @Nullable
    public Predicate<String> fxSource;

    public DevilEntity(EntityType<? extends DevilEntity> type, Level level) {
        super(type, level);
        DevilSpec s = spec();
        this.xpReward = s.xp;
        this.setMaxUpStep(s.stepHeight);
        if (s.flying) {
            this.moveControl = new FlyingMoveControl(this, 20, true);
        }
        if (s.boss) {
            this.bossEvent = (ServerBossEvent) new ServerBossEvent(getDisplayName(), s.bar,
                    BossEvent.BossBarOverlay.NOTCHED_10).setDarkenScreen(false);
            setPersistenceRequired();
        } else {
            this.bossEvent = null;
        }
    }

    public static AttributeSupplier.Builder attributes(DevilSpec s) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, s.health)
                .add(Attributes.ATTACK_DAMAGE, s.damage)
                .add(Attributes.MOVEMENT_SPEED, s.speed)
                .add(Attributes.FLYING_SPEED, s.flySpeed)
                .add(Attributes.ARMOR, s.armor)
                .add(Attributes.ARMOR_TOUGHNESS, s.toughness)
                .add(Attributes.KNOCKBACK_RESISTANCE, s.knockbackResist)
                .add(Attributes.FOLLOW_RANGE, s.followRange);
    }

    public HybridType devilType() {
        return ModEntities.devilOf(getType());
    }

    public DevilSpec spec() {
        return DevilSpecs.of(devilType());
    }

    public float damageScale() {
        return spec().damageScale;
    }

    public boolean isPuppet() {
        return owner != null;
    }

    // ------------------------------------------------------------------ AI
    @Override
    protected void registerGoals() {
        DevilSpec s = spec();
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new DevilMoveGoal(this));
        if (!s.stationary) {
            goalSelector.addGoal(6, s.flying ? new WaterAvoidingRandomFlyingGoal(this, 0.8)
                    : new WaterAvoidingRandomStrollGoal(this, 0.8));
        }
        goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 24f));
        goalSelector.addGoal(8, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this, DevilEntity.class));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        // devils prey on people
        targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        if (spec().flying) {
            FlyingPathNavigation nav = new FlyingPathNavigation(this, level);
            nav.setCanOpenDoors(false);
            nav.setCanFloat(true);
            nav.setCanPassDoors(true);
            return nav;
        }
        return super.createNavigation(level);
    }

    /** The moves this devil fights with (slot 0, the manifestation, and blood drinking are for players). */
    public List<DevilAbility> moves() {
        List<DevilAbility> out = new ArrayList<>();
        for (Ability a : devilType().abilities()) {
            if (a instanceof DevilAbility d && d.mobUse) {
                out.add(d);
            }
        }
        return out;
    }

    public void startMove(DevilAbility move, int index, LivingEntity target) {
        AbilityRun run = new AbilityRun(move, index);
        run.duration = move.duration();
        run.target = target;
        activeRun = run;
        move.begin(this, run);
        if (!move.geoAnim().isEmpty()) {
            triggerAnim("action", move.geoAnim());
        }
        if (!move.fxGroup().isEmpty()) {
            setFx(move.fxGroup(), run.duration);
        }
    }

    private void tickRun() {
        AbilityRun run = activeRun;
        if (run == null) {
            return;
        }
        DevilAbility move = (DevilAbility) run.ability;
        if (move.rooted) {
            getNavigation().stop();
            if (run.target instanceof LivingEntity t && t.isAlive()) {
                face(t);
            }
        }
        move.perform(this, run);
        run.tick++;
        if (activeRun == run && run.tick >= run.duration) {
            move.finish(this, run);
            activeRun = null;
        }
    }

    /** Turn the whole body to face the target right away (moves are aimed at it). */
    public void face(Entity target) {
        double dx = target.getX() - getX();
        double dz = target.getZ() - getZ();
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90f;
        setYRot(yaw);
        yBodyRot = yaw;
        yHeadRot = yaw;
        getLookControl().setLookAt(target, 60f, 60f);
    }

    /** Who this devil will never hurt: its own kind and the creatures it has enthralled. */
    public boolean canHarm(LivingEntity e) {
        if (e instanceof DevilEntity d && d.getType() == getType()) {
            return false;
        }
        return !isThrall(e);
    }

    public boolean isThrall(Entity e) {
        CompoundTag tag = e.getPersistentData();
        return tag.hasUUID(THRALL_TAG) && tag.getUUID(THRALL_TAG).equals(getUUID());
    }

    public static void enthrall(Entity e, UUID master) {
        e.getPersistentData().putUUID(THRALL_TAG, master);
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        return super.canAttack(target) && canHarm(target);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        tickRun();
        if (bossEvent != null) {
            bossEvent.setProgress(getHealth() / getMaxHealth());
            // one only called up for a while (Makima out of Princi's zipper) is on your side: no boss bar
            bossEvent.setVisible(getPersistentData().getLong(com.csm.hybrids.ability.devil.SpiderMoves.SUMMONED_UNTIL) == 0);
        }
    }

    // ------------------------------------------------------------------ effect groups (fx_<group>_ bones)
    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        entityData.define(FX, "");
        entityData.define(FX_END, 0);
    }

    public void setFx(String group, int ticks) {
        entityData.set(FX, group);
        entityData.set(FX_END, (int) (level().getGameTime() + ticks));
    }

    public boolean fxActive(String group) {
        if (fxSource != null) {
            return fxSource.test(group);
        }
        return group.equals(entityData.get(FX)) && level().getGameTime() < entityData.get(FX_END);
    }

    // ------------------------------------------------------------------ misc rules
    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return !spec().flying && super.causeFallDamage(distance, multiplier, source);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return !spec().boss && super.removeWhenFarAway(distance);
    }

    @Override
    public boolean canChangeDimensions() {
        return !spec().boss;
    }

    @Override
    protected void tickDeath() {
        ++deathTime;
        if (deathTime >= (spec().boss ? 40 : 24) && !level().isClientSide() && !isRemoved()) {
            level().broadcastEntityEvent(this, (byte) 60);
            remove(RemovalReason.KILLED);
        }
    }

    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        if (bossEvent != null) {
            bossEvent.addPlayer(player);
        }
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer player) {
        super.stopSeenByPlayer(player);
        if (bossEvent != null) {
            bossEvent.removePlayer(player);
        }
    }

    @Override
    public void setCustomName(@Nullable net.minecraft.network.chat.Component name) {
        super.setCustomName(name);
        if (bossEvent != null) {
            bossEvent.setName(getDisplayName());
        }
    }

    // ------------------------------------------------------------------ GeckoLib
    /** Is it walking/flying (puppets follow the player they stand in for). */
    protected boolean moving(AnimationState<DevilEntity> state) {
        if (owner != null) {
            return owner.walkAnimation.speed() > 0.08f || owner.getDeltaMovement().horizontalDistanceSqr() > 0.003;
        }
        return state.isMoving() || (spec().flying && getDeltaMovement().lengthSqr() > 0.003);
    }

    protected PlayState baseAnim(AnimationState<DevilEntity> state) {
        if (isDeadOrDying() || (owner != null && owner.isDeadOrDying())) {
            return state.setAndContinue(DEATH);
        }
        return state.setAndContinue(moving(state) ? MOVE : IDLE);
    }

    /** Triggerable one-shot animations: every move's, plus manifesting and retracting (player forms). */
    protected List<String> actionAnims() {
        List<String> out = new ArrayList<>(List.of("manifest", "retract", "drink"));
        for (Ability a : devilType().abilities()) {
            if (!a.geoAnim().isEmpty() && !out.contains(a.geoAnim())) {
                out.add(a.geoAnim());
            }
        }
        return out;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "base", 4, this::baseAnim));
        AnimationController<DevilEntity> action = new AnimationController<>(this, "action", 2, s -> PlayState.STOP);
        for (String anim : actionAnims()) {
            action.triggerableAnim(anim, RawAnimation.begin().thenPlay(anim));
        }
        controllers.add(action);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
