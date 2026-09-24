package com.csm.hybrids.ability.blood;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.SpearEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Power, the Blood Fiend. She shapes her own blood into weapons - a giant hammer, spears, a scythe - and on contact can
 * seize the blood inside someone else. Gorged on blood her horns grow and multiply and every weapon hits harder.
 */
public final class BloodAbilities {

    /** Blood weapons hit harder once she has gorged (devil nature unleashed). */
    static float power(HybridData data, float base) {
        return data.isTransformed() ? base * 1.4f : base;
    }

    /** A giant hammer of blood, swung over her head and slammed down. */
    public static class BloodHammer extends Ability {
        public BloodHammer() {
            super(HybridType.BLOOD, "blood_hammer");
            anyForm();
            timing(20, 40);
            cost(4);
            anim("blood_hammer", "hammer");
            fx("hammer");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 2) {
                AbilityUtil.sound(player, ModSounds.BLOOD_FORM.get(), 1f, 0.8f);
                AbilityUtil.blood(level, AbilityUtil.handPos(player, true, 0.2), 16, 0.2);
            }
            if (run.tick != 11) {
                return;
            }
            Vec3 look = player.getLookAngle();
            Vec3 at = player.position().add(look.x * 2.6, 0, look.z * 2.6);
            float radius = data.isTransformed() ? 4.5f : 3.5f;
            AbilityUtil.sound(player, ModSounds.BLOOD_SLAM.get(), 1.5f, 0.8f);
            Fx.shockwave(level, at.add(0, 0.02, 0), radius * 1.2, Fx.BLOOD_RING);
            Fx.impact(level, at.add(0, 0.5, 0), 2.2);
            AbilityUtil.blood(level, at.add(0, 0.3, 0), 60, 0.6);
            Fx.bloodSpray(level, at.add(0, 0.2, 0), new Vec3(0, 1, 0), 30, 0.6);
            Fx.clods(level, at, 14, 0.25);
            for (LivingEntity e : AbilityUtil.inRadius(player, at.add(0, 0.8, 0), radius)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, power(data, 14f))) {
                    AbilityUtil.push(e, at, 0.8, 0.55);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 20, 0.3);
                }
            }
        }
    }

    /** Forms a spear of blood and hurls it. It bursts back into blood where it lands. */
    public static class BloodSpear extends Ability {
        public BloodSpear() {
            super(HybridType.BLOOD, "blood_spear");
            anyForm();
            timing(12, 25);
            cost(2);
            anim("blood_spear", "spear");
            fx("bspear");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 1) {
                AbilityUtil.sound(player, ModSounds.BLOOD_FORM.get(), 0.8f, 1.2f);
            }
            if (run.tick != 6) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 from = AbilityUtil.handPos(player, true, 0.8).add(0, 0.3, 0);
            EntityHitResult aim = AbilityUtil.raycastEntity(player, 64);
            Vec3 to = aim != null ? aim.getEntity().getBoundingBox().getCenter()
                    : player.getEyePosition().add(player.getLookAngle().scale(64));
            SpearEntity spear = new SpearEntity(level, player, SpearEntity.THROWN, power(data, 12f),
                    data.isTransformed() ? 2 : 0, 0.9f).blood();
            spear.setPos(from.x, from.y, from.z);
            Vec3 d = to.subtract(from);
            spear.shoot(d.x, d.y, d.z, 3.2f, 0f);
            level.addFreshEntity(spear);
            AbilityUtil.blood(level, from, 10, 0.1);
            AbilityUtil.sound(player, ModSounds.SPEAR_THROW.get(), 1.1f, 1.2f);
        }
    }

    /** A wide sweep of a blood scythe; the wounds keep bleeding. */
    public static class BloodScythe extends Ability {
        public BloodScythe() {
            super(HybridType.BLOOD, "blood_scythe");
            anyForm();
            timing(18, 45);
            cost(4);
            anim("blood_scythe", "scythe");
            fx("scythe");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 2) {
                AbilityUtil.sound(player, ModSounds.BLOOD_FORM.get(), 1f, 1f);
            }
            if (run.tick != 9) {
                return;
            }
            Vec3 look = player.getLookAngle();
            Vec3 right = AbilityUtil.right(player);
            for (int k = -2; k <= 2; k++) {
                Vec3 dir = look.add(right.scale(k * 0.45)).normalize();
                Fx.slash(level, player.getEyePosition().add(dir.scale(2.2)).add(0, -0.4, 0), dir.cross(new Vec3(0, 1, 0)), 1.8);
            }
            AbilityUtil.sound(player, ModSounds.KATANA_SLASH.get(), 1.1f, 0.7f);
            for (LivingEntity e : AbilityUtil.inCone(player, 5.5, 70)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, power(data, 10f))) {
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WITHER, 60, 0)));
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.3);
                    Fx.bloodSpray(level, e.getBoundingBox().getCenter(), right.scale(-1), 12, 0.4);
                }
            }
        }
    }

    /** Touch a target and seize the blood inside it: it is torn out of them and into her. */
    public static class BloodControl extends Ability {
        public BloodControl() {
            super(HybridType.BLOOD, "blood_control");
            anyForm();
            timing(18, 90);
            anim("blood_control", "control");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 4) {
                EntityHitResult hit = AbilityUtil.raycastEntity(player, 5);
                if (hit != null && hit.getEntity() instanceof LivingEntity target) {
                    run.target = target;
                    target.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 4)));
                    AbilityUtil.sound(player, ModSounds.BLOOD_FORM.get(), 1.2f, 0.6f);
                }
            }
            if (run.target instanceof LivingEntity target && target.isAlive() && run.tick >= 5 && run.tick <= 14) {
                Vec3 c = target.getBoundingBox().getCenter();
                Vec3 to = player.getEyePosition().add(0, -0.4, 0);
                // streams of blood pulled out of the target into her
                Fx.bloodSpray(level, c, to.subtract(c).normalize(), 6, 0.35 + c.distanceTo(to) * 0.08);
                if (run.tick % 3 == 0) {
                    AbilityUtil.hurtIgnoringIFrames(player, target, power(data, 3f));
                    player.heal(1.5f);
                    HybridLogic.addBlood(player, 4f);
                }
            }
        }
    }

    /**
     * Thousand Tera Blood Rain: blades of blood fall out of the sky onto the spot she is looking at.
     * Needs her gorged, devil-side state.
     */
    public static class BloodRain extends Ability {
        public BloodRain() {
            super(HybridType.BLOOD, "blood_rain");
            timing(34, 200);
            cost(14);
            anim("blood_rain", "rain");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 4) {
                HitResult hit = AbilityUtil.raycastBlock(player, 40);
                run.vec = hit.getType() == HitResult.Type.MISS ? player.getEyePosition().add(player.getLookAngle().scale(20))
                        : hit.getLocation();
                AbilityUtil.sound(player, ModSounds.BLOOD_RAIN.get(), 1.6f, 1f);
                AbilityUtil.blood(level, player.getEyePosition().add(0, 0.8, 0), 40, 0.5);
            }
            if (run.vec == null || run.tick < 8 || run.tick > 30) {
                return;
            }
            for (int k = 0; k < 3; k++) {
                double r = 5.5 * Math.sqrt(level.random.nextDouble());
                double a = level.random.nextDouble() * Math.PI * 2;
                Vec3 ground = run.vec.add(Math.cos(a) * r, 0, Math.sin(a) * r);
                Vec3 sky = ground.add(level.random.nextGaussian() * 0.6, 14 + level.random.nextDouble() * 4,
                        level.random.nextGaussian() * 0.6);
                SpearEntity blade = new SpearEntity(level, player, SpearEntity.THROWN, 7f, 0, 0.55f).blood();
                blade.setPos(sky.x, sky.y, sky.z);
                Vec3 d = ground.subtract(sky);
                blade.shoot(d.x, d.y, d.z, 2.2f, 0f);
                level.addFreshEntity(blade);
            }
        }
    }

    private BloodAbilities() {
    }
}
