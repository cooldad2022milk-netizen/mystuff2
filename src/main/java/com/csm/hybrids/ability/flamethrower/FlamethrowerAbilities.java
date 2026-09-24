package com.csm.hybrids.ability.flamethrower;

import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.NapalmEntity;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Barem Bridge's moves: flamethrower arms, fuel-tank head. */
public final class FlamethrowerAbilities {

    static void flameJet(ServerLevel level, Vec3 from, Vec3 dir, int count, double speed, double spread) {
        Fx.fireJet(level, from, dir, count, speed, spread);
    }

    /** Both arms pour out a roaring stream of fire for three seconds. */
    public static class FlameStream extends Ability {
        public FlameStream() {
            super(HybridType.FLAMETHROWER, "flame_stream");
            timing(60, 90);
            cost(6);
            anim("flame_stream", ""); // flame jets loop via the "flame" fx group
            fx("flame");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 3, 1, false, false, false)));
            if (run.tick < 6) {
                return;
            }
            Vec3 look = player.getLookAngle();
            for (boolean right : new boolean[]{true, false}) {
                flameJet(level, AbilityUtil.handPos(player, right, 1.1), look, 9, 0.75, 0.09);
            }
            if (run.tick % 3 == 0) {
                Vec3 mid = player.getEyePosition().add(look.scale(4));
                Fx.smoke(level, mid.add(0, 0.8, 0), 2, 0.8);
            }
            if (run.tick % 12 == 6) {
                AbilityUtil.sound(player, ModSounds.FLAME_STREAM.get(), 1.2f, 0.9f + level.random.nextFloat() * 0.2f);
            }
            if (run.tick % 4 == 0) {
                for (LivingEntity e : AbilityUtil.inCone(player, 9.0, 18)) {
                    e.setSecondsOnFire(6);
                    AbilityUtil.hurtIgnoringIFrames(player, e, 3f);
                }
            }
            if (run.tick % 5 == 0) {
                BlockHitResult hit = AbilityUtil.raycastBlock(player, 9);
                if (hit.getType() == HitResult.Type.BLOCK) {
                    AbilityUtil.ignite(level, hit.getBlockPos().relative(hit.getDirection()));
                }
            }
        }
    }

    /** Lobs a glob of burning fuel that explodes and leaves the ground on fire. */
    public static class NapalmShot extends Ability {
        public NapalmShot() {
            super(HybridType.FLAMETHROWER, "napalm_shot");
            timing(12, 60);
            cost(4);
            anim("flame_napalm", "napalm");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 5) {
                NapalmEntity napalm = new NapalmEntity(player.level(), player);
                Vec3 from = AbilityUtil.handPos(player, true, 1.2);
                napalm.setPos(from.x, from.y, from.z);
                Vec3 look = player.getLookAngle();
                napalm.shoot(look.x, look.y + 0.08, look.z, 1.7f, 0.5f);
                player.level().addFreshEntity(napalm);
                AbilityUtil.sound(player, ModSounds.FLAME_BURST.get(), 1f, 1.3f);
                flameJet(player.serverLevel(), from, look, 20, 0.5, 0.2);
            }
        }
    }

    /** Slam both flamethrowers into the ground: a ring of fire blasts outward. */
    public static class InfernoBurst extends Ability {
        public InfernoBurst() {
            super(HybridType.FLAMETHROWER, "inferno_burst");
            timing(20, 200);
            cost(10);
            anim("flame_burst", "burst");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 10) {
                AbilityUtil.sound(player, ModSounds.FLAME_BURST.get(), 1.6f, 0.8f);
                for (int ring = 1; ring <= 3; ring++) {
                    Fx.fireBurst(level, player.position().add(0, 0.3, 0), 36, 0.25 * ring);
                }
                Fx.shockwave(level, player.position(), 6.5, Fx.FIRE_RING);
                Fx.impact(level, player.position().add(0, 0.8, 0), 2.6);
                Fx.smoke(level, player.position().add(0, 0.6, 0), 14, 1.4);
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 0.8, 0), 6.0)) {
                    AbilityUtil.hurtIgnoringIFrames(player, e, 12f);
                    e.setSecondsOnFire(8);
                    AbilityUtil.push(e, player.position(), 1.4, 0.45);
                }
                if (AbilityUtil.griefing(level)) {
                    for (int i = 0; i < 6; i++) {
                        double a = level.random.nextDouble() * Math.PI * 2;
                        double r = 1.5 + level.random.nextDouble() * 3.5;
                        BlockPos pos = BlockPos.containing(player.getX() + Math.cos(a) * r, player.getY(), player.getZ() + Math.sin(a) * r);
                        AbilityUtil.ignite(level, pos);
                    }
                }
            }
        }
    }

    /** Spin with both flamethrowers roaring, engulfing everything around you - a whole floor goes up. */
    public static class Conflagration extends Ability {
        public Conflagration() {
            super(HybridType.FLAMETHROWER, "conflagration");
            timing(40, 400);
            cost(20);
            anim("flame_conflagration", "");
            fx("flame");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick < 8 || run.tick > 36) {
                return;
            }
            double progress = (run.tick - 8) / 28.0;
            double radius = 2 + progress * 8;
            double spin = run.tick * 0.55;
            for (int arm = 0; arm < 2; arm++) {
                double a = spin + arm * Math.PI;
                Vec3 dir = new Vec3(Math.cos(a), -0.08, Math.sin(a));
                flameJet(level, player.position().add(0, 1.2, 0).add(dir.scale(0.6)), dir, 14, 0.8, 0.12);
            }
            if (run.tick % 4 == 0) {
                AbilityUtil.sound(player, ModSounds.FLAME_STREAM.get(), 1.3f, 0.8f);
            }
            if (run.tick % 6 == 0) {
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 1, 0), radius)) {
                    e.setSecondsOnFire(10);
                    AbilityUtil.hurtIgnoringIFrames(player, e, 3f);
                }
            }
            if (run.tick % 4 == 0 && AbilityUtil.griefing(level)) {
                for (int i = 0; i < 2; i++) {
                    double a = level.random.nextDouble() * Math.PI * 2;
                    double r = 2 + level.random.nextDouble() * (radius - 2);
                    BlockPos pos = BlockPos.containing(player.getX() + Math.cos(a) * r, player.getY() + 0.2, player.getZ() + Math.sin(a) * r);
                    for (int dy = 1; dy >= -2; dy--) {
                        BlockPos p = pos.above(dy);
                        if (level.isEmptyBlock(p) && !level.isEmptyBlock(p.below())) {
                            AbilityUtil.ignite(level, p);
                            break;
                        }
                    }
                }
            }
        }
    }

    /** Pressing the molar again restores his body to peak condition. */
    public static class MolarRegeneration extends Ability {
        public MolarRegeneration() {
            super(HybridType.FLAMETHROWER, "molar_regeneration");
            timing(14, 600);
            cost(25);
            anim("flame_regen", "regen");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 5) {
                AbilityUtil.sound(player, ModSounds.MOLAR_CLICK.get(), 1.3f, 1.1f);
            }
            if (run.tick == 7) {
                player.setHealth(player.getMaxHealth());
                player.clearFire();
                player.getActiveEffects().stream()
                        .filter(e -> e.getEffect().getCategory() == MobEffectCategory.HARMFUL)
                        .map(MobEffectInstance::getEffect).toList()
                        .forEach(player::removeEffect);
                player.getFoodData().eat(6, 0.6f);
                Vec3 c = player.position().add(0, 1, 0);
                Fx.fireBurst(level, c.add(0, -0.8, 0), 30, 0.12);
                Fx.embers(level, c, 30, 0.6);
                Fx.shockwave(level, player.position(), 2.5, Fx.FIRE_RING);
                AbilityUtil.sound(player, ModSounds.FLAME_IGNITE.get(), 1f, 1.2f);
            }
        }
    }

    private FlamethrowerAbilities() {
    }
}
