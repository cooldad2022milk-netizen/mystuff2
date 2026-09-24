package com.csm.hybrids.entity;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModParticles;
import com.csm.hybrids.registry.ModSounds;
import it.unimi.dsi.fastutil.ints.IntOpenHashSet;
import it.unimi.dsi.fastutil.ints.IntSet;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * A spear made by the Spear Hybrid (or, as the BLOOD variant, one of Power's blood spears). THROWN spears fly dead straight (he can hit targets hundreds of metres up),
 * pierce, and stick into whatever stops them. ERUPT spears burst out of the ground and skewer anything above.
 */
public class SpearEntity extends Projectile implements GeoEntity {
    public static final int THROWN = 0;
    public static final int STUCK = 1;
    public static final int ERUPT = 2;
    private static final EntityDataAccessor<Integer> MODE = SynchedEntityData.defineId(SpearEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> SCALE = SynchedEntityData.defineId(SpearEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Integer> VARIANT = SynchedEntityData.defineId(SpearEntity.class, EntityDataSerializers.INT);
    public static final int IRON = 0;
    /** Power's blood spear: bursts into blood instead of sticking. */
    public static final int BLOOD = 1;
    private static final RawAnimation RISE = RawAnimation.begin().thenPlayAndHold("rise");

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final IntSet hitIds = new IntOpenHashSet();
    private float damage = 20f;
    private int pierceLeft = 3;
    private int life;

    public SpearEntity(EntityType<? extends SpearEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public SpearEntity(Level level, LivingEntity owner, int mode, float damage, int pierce, float scale) {
        this(ModEntities.SPEAR.get(), level);
        setOwner(owner);
        this.damage = damage;
        this.pierceLeft = pierce;
        this.entityData.set(MODE, mode);
        this.entityData.set(SCALE, scale);
    }

    @Override
    protected void defineSynchedData() {
        this.entityData.define(MODE, THROWN);
        this.entityData.define(SCALE, 1f);
        this.entityData.define(VARIANT, IRON);
    }

    public int mode() {
        return this.entityData.get(MODE);
    }

    public float scale() {
        return this.entityData.get(SCALE);
    }

    public int variant() {
        return this.entityData.get(VARIANT);
    }

    public SpearEntity blood() {
        this.entityData.set(VARIANT, BLOOD);
        return this;
    }

    @Override
    public void tick() {
        super.tick();
        life++;
        switch (mode()) {
            case THROWN -> flyTick();
            case STUCK -> {
                setDeltaMovement(Vec3.ZERO);
                if (!level().isClientSide && life > 100) {
                    discard();
                }
            }
            case ERUPT -> {
                setDeltaMovement(Vec3.ZERO);
                if (!level().isClientSide) {
                    if (life == 3 && getOwner() instanceof ServerPlayer sp) {
                        ServerLevel sl = (ServerLevel) level();
                        Fx.shards(sl, position(), 6, 0.3);
                        Fx.smoke(sl, position(), 3, 0.3);
                        for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, new AABB(position(), position()).inflate(1.2, 2.2, 1.2),
                                e -> AbilityUtil.canHit(sp, e))) {
                            if (AbilityUtil.hurtIgnoringIFrames(sp, e, damage)) {
                                e.setDeltaMovement(e.getDeltaMovement().add(0, 0.7, 0));
                                e.hurtMarked = true;
                                AbilityUtil.blood(sl, e.getBoundingBox().getCenter(), 20, 0.25);
                            }
                        }
                    }
                    if (life > 40) {
                        discard();
                    }
                }
            }
            default -> {
            }
        }
    }

    private void flyTick() {
        Vec3 pos = position();
        Vec3 vel = getDeltaMovement();
        if (!level().isClientSide) {
            ServerLevel sl = (ServerLevel) level();
            HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
            if (hit instanceof EntityHitResult ehr) {
                Entity e = ehr.getEntity();
                if (hitIds.add(e.getId())) {
                    strike(sl, e);
                }
                if (--pierceLeft < 0) {
                    discard();
                    return;
                }
            } else if (hit instanceof BlockHitResult bhr && hit.getType() == HitResult.Type.BLOCK) {
                if (variant() == BLOOD) {
                    // blood weapons burst back into blood
                    AbilityUtil.blood(sl, bhr.getLocation(), 18, 0.25);
                    Fx.bloodSpray(sl, bhr.getLocation(), vel.scale(-1).normalize(), 8, 0.3);
                    sl.playSound(null, bhr.getLocation().x, bhr.getLocation().y, bhr.getLocation().z,
                            ModSounds.BLOOD_SLAM.get(), SoundSource.PLAYERS, 0.5f, 1.6f);
                    discard();
                    return;
                }
                Vec3 at = bhr.getLocation().subtract(vel.normalize().scale(0.3));
                setPos(at.x, at.y, at.z);
                this.entityData.set(MODE, STUCK);
                life = 0;
                Fx.sparks(sl, bhr.getLocation(), vel.scale(-1).normalize(), 8, 0.35);
                Fx.shards(sl, bhr.getLocation(), 4, 0.15);
                sl.playSound(null, at.x, at.y, at.z, ModSounds.SPEAR_IMPACT.get(), SoundSource.PLAYERS, 1f, 1f);
                return;
            }
            if (life > 80) {
                discard();
                return;
            }
        } else if (life > 1) {
            level().addParticle(ModParticles.SPEED_LINE.get(), pos.x, pos.y, pos.z, -vel.x * 0.9, -vel.y * 0.9, -vel.z * 0.9);
            if (variant() == BLOOD && life % 2 == 0) {
                level().addParticle(ModParticles.BLOOD.get(), pos.x, pos.y, pos.z, 0, 0, 0);
            }
        }
        setPos(pos.x + vel.x, pos.y + vel.y, pos.z + vel.z);
        updateRotation();
    }

    private void strike(ServerLevel level, Entity e) {
        Entity owner = getOwner();
        if (e.hurt(damageSources().mobProjectile(this, owner instanceof LivingEntity l ? l : null), AbilityUtil.dmg(damage))) {
            Vec3 c = e.getBoundingBox().getCenter();
            AbilityUtil.blood(level, c, 26, 0.25);
            Fx.bloodSpray(level, c, getDeltaMovement().normalize(), 14, 0.45);
            e.setDeltaMovement(e.getDeltaMovement().add(getDeltaMovement().normalize().scale(0.6)));
            e.hurtMarked = true;
            level.playSound(null, c.x, c.y, c.z, ModSounds.SPEAR_IMPACT.get(), SoundSource.PLAYERS, 1.1f, 0.8f);
        }
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && entity != getOwner() && !hitIds.contains(entity.getId())
                && (!(getOwner() instanceof ServerPlayer sp) || AbilityUtil.canHit(sp, entity));
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 160 * 160;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 0,
                state -> mode() == ERUPT ? state.setAndContinue(RISE) : PlayState.STOP));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
