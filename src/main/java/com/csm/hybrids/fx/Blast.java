package com.csm.hybrids.fx;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.level.BlockEvent;
import org.jetbrains.annotations.Nullable;

/**
 * The Bomb Devil's explosions. Custom instead of vanilla explosions so they use the mod's own particles,
 * and because Reze is never hurt by her own blasts.
 */
public final class Blast {

    /**
     * @param owner       the hybrid who caused it (immune); may be null
     * @param cause       the direct cause (projectile) or null
     * @param breakBlocks crater weak blocks (only when griefing is allowed)
     */
    public static void detonate(ServerLevel level, @Nullable ServerPlayer owner, @Nullable Entity cause, Vec3 pos,
                                float radius, float damage, boolean breakBlocks) {
        AABB box = new AABB(pos, pos).inflate(radius);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, box)) {
            if (owner != null && (e == owner || !AbilityUtil.canHit(owner, e))) {
                continue;
            }
            double d = e.getBoundingBox().getCenter().distanceTo(pos);
            if (d > radius) {
                continue;
            }
            float falloff = (float) (1.0 - d / radius * 0.6);
            Entity direct = cause != null ? cause : owner;
            DamageSource src = level.damageSources().explosion(direct, owner);
            e.hurt(src, AbilityUtil.dmg(damage * falloff));
            AbilityUtil.push(e, pos, 0.4 + 1.1 * falloff, 0.15 + 0.35 * falloff);
        }
        Fx.explosion(level, pos, radius);
        level.playSound(null, pos.x, pos.y, pos.z, radius >= 3.5f ? ModSounds.BOMB_EXPLOSION.get() : ModSounds.BOMB_BLAST.get(),
                SoundSource.PLAYERS, 1.2f + radius * 0.12f, 0.85f + level.random.nextFloat() * 0.25f);
        if (breakBlocks && AbilityUtil.griefing(level)) {
            crater(level, owner, pos, radius * 0.6f);
        }
    }

    private static void crater(ServerLevel level, @Nullable ServerPlayer owner, Vec3 c, float r) {
        int ir = Mth.ceil(r);
        BlockPos base = BlockPos.containing(c);
        for (int x = -ir; x <= ir; x++) {
            for (int y = -ir; y <= ir; y++) {
                for (int z = -ir; z <= ir; z++) {
                    BlockPos p = base.offset(x, y, z);
                    double d2 = Vec3.atCenterOf(p).distanceToSqr(c);
                    if (d2 > r * r || level.random.nextFloat() < d2 / (r * r) * 0.5) {
                        continue;
                    }
                    BlockState state = level.getBlockState(p);
                    if (state.isAir() || state.getDestroySpeed(level, p) < 0 || state.getBlock().getExplosionResistance() > 4.0f) {
                        continue;
                    }
                    if (owner != null && MinecraftForge.EVENT_BUS.post(new BlockEvent.BreakEvent(level, p, state, owner))) {
                        continue;
                    }
                    level.destroyBlock(p, level.random.nextFloat() < 0.2f);
                }
            }
        }
    }

    private Blast() {
    }
}
