package com.csm.hybrids.entity;

import com.csm.hybrids.fx.Blast;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModParticles;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Reze blows her own bomb head off and throws it. It tumbles through the air, fuse sputtering, and goes off with
 * her biggest explosion. (A new head grows back on the thrower.)
 */
public class HeadBombEntity extends Projectile implements GeoEntity {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private int life;

    public HeadBombEntity(EntityType<? extends HeadBombEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public HeadBombEntity(Level level, LivingEntity owner) {
        this(ModEntities.HEAD_BOMB.get(), level);
        setOwner(owner);
    }

    @Override
    protected void defineSynchedData() {
    }

    @Override
    public void tick() {
        super.tick();
        Vec3 pos = position();
        Vec3 vel = getDeltaMovement();
        if (!level().isClientSide) {
            if (life % 8 == 0) {
                level().playSound(null, pos.x, pos.y, pos.z, ModSounds.BOMB_FUSE.get(), SoundSource.PLAYERS, 0.8f, 1.2f);
            }
            HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
            if (hit.getType() != HitResult.Type.MISS || ++life > 80) {
                Vec3 at = hit.getType() != HitResult.Type.MISS ? hit.getLocation() : pos;
                Blast.detonate((ServerLevel) level(), getOwner() instanceof ServerPlayer sp ? sp : null, this, at, 5.2f, 20f, true);
                discard();
                return;
            }
        } else {
            level().addParticle(ModParticles.SPARK.get(), pos.x, pos.y + 0.3, pos.z, random.nextGaussian() * 0.1,
                    0.1 + random.nextDouble() * 0.1, random.nextGaussian() * 0.1);
            level().addParticle(ModParticles.SMOKE.get(), pos.x, pos.y + 0.3, pos.z, 0, 0.02, 0);
        }
        setPos(pos.x + vel.x, pos.y + vel.y, pos.z + vel.z);
        setDeltaMovement(vel.x * 0.99, vel.y - 0.045, vel.z * 0.99);
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && entity != getOwner();
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
