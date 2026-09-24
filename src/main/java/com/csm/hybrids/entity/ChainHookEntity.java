package com.csm.hybrids.entity;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The chain Denji fires out of his forearm. Hooks terrain to reel him in, or wraps a target and drags it over.
 */
public class ChainHookEntity extends Projectile {
    public static final int FLYING = 0;
    public static final int ANCHORED = 1;
    public static final int BOUND = 2;
    private static final EntityDataAccessor<Integer> STATE = SynchedEntityData.defineId(ChainHookEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> HOOKED = SynchedEntityData.defineId(ChainHookEntity.class, EntityDataSerializers.INT);

    private int life;
    private int pullTicks;

    public ChainHookEntity(EntityType<? extends ChainHookEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public ChainHookEntity(Level level, LivingEntity owner) {
        this(ModEntities.CHAIN_HOOK.get(), level);
        setOwner(owner);
    }

    @Override
    protected void defineSynchedData() {
        this.entityData.define(STATE, FLYING);
        this.entityData.define(HOOKED, -1);
    }

    public int state() {
        return this.entityData.get(STATE);
    }

    @Override
    public void tick() {
        super.tick();
        Entity owner = getOwner();
        boolean server = !level().isClientSide;
        if (server && (owner == null || !owner.isAlive() || owner.level() != level() || owner.distanceToSqr(this) > 48 * 48)) {
            discard();
            return;
        }
        switch (state()) {
            case FLYING -> {
                if (server) {
                    HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
                    if (hit.getType() != HitResult.Type.MISS) {
                        onHit(hit);
                    }
                }
                if (state() == FLYING) {
                    Vec3 v = getDeltaMovement();
                    setPos(getX() + v.x, getY() + v.y, getZ() + v.z);
                    updateRotation();
                    if (server && ++life > 16) {
                        discard();
                    }
                }
            }
            case ANCHORED -> {
                setDeltaMovement(Vec3.ZERO);
                if (server && owner instanceof ServerPlayer sp) {
                    Vec3 to = position().subtract(sp.position().add(0, 1.0, 0));
                    if (to.length() < 2.0 || ++pullTicks > 40 || sp.isShiftKeyDown()) {
                        discard();
                        return;
                    }
                    Vec3 v = to.normalize().scale(1.3);
                    sp.setDeltaMovement(v.x, v.y + 0.1, v.z);
                    sp.hurtMarked = true;
                    sp.fallDistance = 0;
                }
            }
            case BOUND -> {
                Entity target = level().getEntity(this.entityData.get(HOOKED));
                if (target == null || !target.isAlive()) {
                    if (server) {
                        discard();
                    }
                    return;
                }
                setPos(target.getX(), target.getY(0.6), target.getZ());
                if (server && owner != null) {
                    Vec3 to = owner.position().subtract(target.position());
                    if (to.length() < 2.6 || ++pullTicks > 30) {
                        if (target instanceof LivingEntity living) {
                            living.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2)));
                            if (owner instanceof ServerPlayer sp) {
                                AbilityUtil.hurtIgnoringIFrames(sp, living, 3f);
                            }
                        }
                        discard();
                        return;
                    }
                    Vec3 v = to.normalize().scale(1.05);
                    target.setDeltaMovement(v.x, Math.max(v.y, 0) + 0.12, v.z);
                    target.hurtMarked = true;
                }
            }
            default -> {
            }
        }
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && entity instanceof LivingEntity && entity != getOwner();
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        this.entityData.set(STATE, BOUND);
        this.entityData.set(HOOKED, result.getEntity().getId());
        playHit();
        if (getOwner() instanceof ServerPlayer sp && result.getEntity() instanceof LivingEntity living) {
            AbilityUtil.hurt(sp, living, 3f);
            AbilityUtil.blood((ServerLevel) level(), living.getBoundingBox().getCenter(), 10, 0.2);
        }
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        Vec3 p = result.getLocation();
        setPos(p.x, p.y, p.z);
        this.entityData.set(STATE, ANCHORED);
        playHit();
    }

    private void playHit() {
        level().playSound(null, getX(), getY(), getZ(), ModSounds.CHAIN_HIT.get(), SoundSource.PLAYERS, 1f, 1f);
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 96 * 96;
    }
}
