package com.csm.hybrids.entity;

import com.csm.hybrids.fx.Blast;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModParticles;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Reze flicks her fingers: a spark that detonates on whatever it touches. */
public class SparkBombEntity extends Projectile {
    private int life;

    public SparkBombEntity(EntityType<? extends SparkBombEntity> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public SparkBombEntity(Level level, LivingEntity owner) {
        this(ModEntities.SPARK_BOMB.get(), level);
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
            HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
            if (hit.getType() != HitResult.Type.MISS || ++life > 60) {
                Vec3 at = hit.getType() != HitResult.Type.MISS ? hit.getLocation() : pos;
                Blast.detonate((ServerLevel) level(), getOwner() instanceof ServerPlayer sp ? sp : null, this, at, 2.6f, 10f, true);
                discard();
                return;
            }
        } else {
            for (int i = 0; i < 3; i++) {
                Vec3 p = pos.add(vel.scale(i / 3.0));
                level().addParticle(i == 0 ? ModParticles.CHARGE.get() : ModParticles.EMBER.get(), p.x, p.y, p.z, 0, 0, 0);
            }
            level().addParticle(ModParticles.SPARK.get(), pos.x, pos.y, pos.z, random.nextGaussian() * 0.08,
                    0.05 + random.nextDouble() * 0.08, random.nextGaussian() * 0.08);
        }
        setPos(pos.x + vel.x, pos.y + vel.y, pos.z + vel.z);
        setDeltaMovement(vel.x * 0.99, vel.y - 0.02, vel.z * 0.99);
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        return super.canHitEntity(entity) && entity != getOwner();
    }
}
