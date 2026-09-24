package com.csm.hybrids.entity;

import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.registry.ModEntities;
import it.unimi.dsi.fastutil.ints.IntOpenHashSet;
import it.unimi.dsi.fastutil.ints.IntSet;
import net.minecraft.core.BlockPos;
import com.csm.hybrids.registry.ModParticles;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.level.BlockEvent;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Bolt from the Crossbow Hybrid's forearm crossbows. The overdrawn "piercing" variant never stops:
 * it tears a perfectly round tunnel through blocks and everything standing in the way.
 */
public class CrossbowBoltEntity extends Projectile implements GeoEntity {
    private static final EntityDataAccessor<Boolean> PIERCING = SynchedEntityData.defineId(CrossbowBoltEntity.class, EntityDataSerializers.BOOLEAN);
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final IntSet hitIds = new IntOpenHashSet();
    private float damage = 6f;
    private int pierceLeft;
    private int life;
    private Vec3 origin;

    public CrossbowBoltEntity(EntityType<? extends CrossbowBoltEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public CrossbowBoltEntity(Level level, LivingEntity owner, float damage, int pierce, boolean piercing) {
        this(ModEntities.CROSSBOW_BOLT.get(), level);
        setOwner(owner);
        this.damage = damage;
        this.pierceLeft = pierce;
        this.entityData.set(PIERCING, piercing);
    }

    @Override
    protected void defineSynchedData() {
        this.entityData.define(PIERCING, false);
    }

    public boolean isPiercing() {
        return this.entityData.get(PIERCING);
    }

    @Override
    public void tick() {
        super.tick();
        if (origin == null) {
            origin = position();
        }
        Vec3 pos = position();
        Vec3 vel = getDeltaMovement();
        Vec3 next = pos.add(vel);
        if (!level().isClientSide) {
            ServerLevel level = (ServerLevel) level();
            if (isPiercing()) {
                AABB sweep = getBoundingBox().expandTowards(vel).inflate(1.1);
                for (Entity e : level.getEntities(this, sweep, this::canHitEntity)) {
                    if (hitIds.add(e.getId())) {
                        strike(e);
                    }
                }
                if (AbilityUtil.griefing(level)) {
                    for (double s = 0; s <= 1.0; s += 0.25) {
                        carve(level, pos.lerp(next, s), 1.3);
                    }
                }
                if (origin.distanceTo(next) > 64 || ++life > 40) {
                    discard();
                    return;
                }
            } else {
                HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
                if (hit instanceof EntityHitResult ehr) {
                    if (hitIds.add(ehr.getEntity().getId())) {
                        strike(ehr.getEntity());
                    }
                    if (--pierceLeft < 0) {
                        discard();
                        return;
                    }
                } else if (hit instanceof BlockHitResult bhr && hit.getType() == HitResult.Type.BLOCK) {
                    Vec3 l = bhr.getLocation();
                    Fx.sparks(level, l, getDeltaMovement().scale(-1).normalize(), 6, 0.3);
                    Fx.shards(level, l, 3, 0.1);
                    level.playSound(null, l.x, l.y, l.z, SoundEvents.ARROW_HIT, SoundSource.PLAYERS, 0.8f, 1.2f);
                    discard();
                    return;
                }
                if (++life > 100) {
                    discard();
                    return;
                }
            }
        } else if (isPiercing()) {
            for (int i = 0; i < 4; i++) {
                Vec3 p = pos.lerp(next, i / 4.0);
                level().addParticle(ModParticles.CHARGE.get(), p.x, p.y, p.z, 0, 0, 0);
                if (i == 0) {
                    level().addParticle(ModParticles.SPEED_LINE.get(), p.x, p.y, p.z, -vel.x * 0.8, -vel.y * 0.8, -vel.z * 0.8);
                }
            }
        } else if (tickCount % 2 == 0) {
            level().addParticle(ModParticles.SPEED_LINE.get(), pos.x, pos.y, pos.z, -vel.x * 0.5, -vel.y * 0.5, -vel.z * 0.5);
        }
        setPos(next.x, next.y, next.z);
        if (!isPiercing()) {
            setDeltaMovement(vel.x * 0.995, vel.y - 0.03, vel.z * 0.995);
        }
        updateRotation();
    }

    private void strike(Entity e) {
        Entity owner = getOwner();
        DamageSource src = damageSources().mobProjectile(this, owner instanceof LivingEntity l ? l : null);
        if (e.hurt(src, AbilityUtil.dmg(damage))) {
            if (e instanceof LivingEntity living) {
                Vec3 v = getDeltaMovement().normalize().scale(isPiercing() ? 0.8 : 0.3);
                living.push(v.x, 0.1, v.z);
                AbilityUtil.blood((ServerLevel) level(), living.getBoundingBox().getCenter(), isPiercing() ? 40 : 12, 0.2);
                Fx.bloodSpray((ServerLevel) level(), living.getBoundingBox().getCenter(), getDeltaMovement().normalize(),
                        isPiercing() ? 24 : 8, 0.4);
                if (isPiercing()) {
                    Fx.impact((ServerLevel) level(), living.getBoundingBox().getCenter(), 1.8);
                }
            }
        }
    }

    /** The bolt's signature: a perfectly circular hole. */
    private void carve(ServerLevel level, Vec3 c, double r) {
        int ir = Mth.ceil(r);
        BlockPos base = BlockPos.containing(c);
        Player player = getOwner() instanceof ServerPlayer sp ? sp : null;
        for (int x = -ir; x <= ir; x++) {
            for (int y = -ir; y <= ir; y++) {
                for (int z = -ir; z <= ir; z++) {
                    BlockPos p = base.offset(x, y, z);
                    if (Vec3.atCenterOf(p).distanceToSqr(c) > r * r) {
                        continue;
                    }
                    BlockState state = level.getBlockState(p);
                    float hardness = state.getDestroySpeed(level, p);
                    if (state.isAir() || hardness < 0 || hardness > 50) {
                        continue;
                    }
                    if (player != null && MinecraftForge.EVENT_BUS.post(new BlockEvent.BreakEvent(level, p, state, player))) {
                        continue;
                    }
                    level.destroyBlock(p, false, this);
                }
            }
        }
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && entity != getOwner() && !hitIds.contains(entity.getId());
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
