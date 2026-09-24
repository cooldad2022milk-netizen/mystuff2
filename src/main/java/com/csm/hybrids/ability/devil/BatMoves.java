package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * The Bat Devil: a hulking bat that drinks blood to heal, flies, and reshapes its maw into a gun barrel to fire a
 * blast of compressed air.
 */
public final class BatMoves {

    public static List<Ability> all() {
        return List.of(new Bite(), new AirCannon(), new Swoop(), new Screech());
    }

    /** Where the bat's mouth is (the barrel's muzzle during the air cannon). */
    static Vec3 mouth(LivingEntity user, double forward) {
        return user.position().add(0, user.getBbHeight() * 0.78, 0).add(AbilityUtil.aim(user).scale(user.getBbWidth() * 0.6
                + forward));
    }

    /** Lunge and bite; the blood it drinks heals it. */
    public static class Bite extends DevilAbility {
        public Bite() {
            super(HybridType.BAT, "bat_bite");
            timing(16, 30);
            cost(0);
            anim("", "bite");
            ai(0, 3, 14);
            mobile();
            reach(5);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            LivingEntity t = target(run);
            Vec3 aim = t != null ? t.getBoundingBox().getCenter().subtract(user.getEyePosition()).normalize()
                    : AbilityUtil.aim(user);
            if (run.tick == 2) {
                // lunge - only as far as the prey
                double reachTo = t != null ? Math.max(0, user.distanceTo(t) - user.getBbWidth() * 0.5 - 1.0) : 2.0;
                double v = Math.min(0.8, reachTo * 0.28);
                user.setDeltaMovement(aim.x * v, aim.y * v * 0.5 + 0.1, aim.z * v);
                user.hurtMarked = true;
            }
            if (run.tick < 5 || run.tick > 9 || run.counter != 0) {
                return;
            }
            float dealt = 0;
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 3.2 + user.getBbWidth() * 0.5, 60)) {
                if (e.getBoundingBox().getCenter().distanceTo(user.getEyePosition()) > 3.4 + user.getBbWidth()) {
                    continue;
                }
                run.counter = 1;
                AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.1f, 1.1f);
                user.setDeltaMovement(user.getDeltaMovement().scale(0.2));
                if (AbilityUtil.hurtIgnoringIFrames(user, e, 12f)) {
                    dealt += 12f;
                    Vec3 c = e.getBoundingBox().getCenter();
                    AbilityUtil.blood(level, c, 30, 0.25);
                    Fx.bloodSpray(level, c, aim.scale(-1), 12, 0.35);
                }
                break;
            }
            if (dealt > 0) {
                user.heal(AbilityUtil.dmg(user, dealt) * 0.5f);
                if (user instanceof ServerPlayer sp) {
                    HybridLogic.addBlood(sp, 10f);
                }
            }
        }
    }

    /** The maw stretches into a barrel: a blast of compressed air that hurls everything in its path. */
    public static class AirCannon extends DevilAbility {
        public AirCannon() {
            super(HybridType.BAT, "bat_air_cannon");
            timing(24, 90);
            cost(8);
            anim("", "blast");
            fx("blast");
            ai(3, 18, 10);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 0.8f, 1.8f);
            }
            if (run.tick > 4 && run.tick < 13 && run.tick % 2 == 0) {
                // air sucked in to be compressed
                Vec3 m = mouth(user, 0.3);
                for (int k = 0; k < 3; k++) {
                    Vec3 from = m.add(level.random.nextGaussian() * 1.2, level.random.nextGaussian() * 1.0,
                            level.random.nextGaussian() * 1.2);
                    Fx.speedLine(level, from, m);
                }
            }
            if (run.tick != 14) {
                return;
            }
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 m = mouth(user, 0.6);
            AbilityUtil.sound(user, ModSounds.GUN_CANNON.get(), 1.4f, 1.4f);
            AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 1.6f, 1.2f);
            double range = 22;
            for (LivingEntity e : coneTargets(user, run, m, aim, range, 20)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 14f);
                double k = 1.0 - Math.min(1.0, e.distanceTo(user) / range) * 0.5;
                e.setDeltaMovement(e.getDeltaMovement().add(aim.x * 2.2 * k, 0.45 + aim.y * k, aim.z * 2.2 * k));
                e.hurtMarked = true;
                Fx.impact(level, e.getBoundingBox().getCenter(), 1.4);
            }
            // the blast: a tunnel of speed lines and rings of pressure along its path
            for (int i = 0; i < 12; i++) {
                double d = 1.0 + i * 1.7;
                Vec3 c = m.add(aim.scale(d));
                Vec3 off = new Vec3(level.random.nextGaussian(), level.random.nextGaussian(), level.random.nextGaussian())
                        .scale(0.25 + d * 0.03);
                Fx.speedLine(level, c.add(off), c.add(off).add(aim.scale(2.5)));
                if (i % 3 == 0) {
                    Fx.shockwave(level, c.add(0, -0.08, 0), 0.8 + d * 0.06, Fx.STEEL_RING);
                }
            }
            Fx.impact(level, m, 1.8);
            user.setDeltaMovement(user.getDeltaMovement().add(aim.scale(-0.5)));
            user.hurtMarked = true;
        }
    }

    /** Dive, snatch the prey, haul it high into the air and let it fall. */
    public static class Swoop extends DevilAbility {
        public Swoop() {
            super(HybridType.BAT, "bat_swoop");
            timing(34, 110);
            cost(10);
            anim("", "swoop");
            ai(2, 14, 8);
            mobile();
            reach(16);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            LivingEntity t = target(run);
            if (run.tick == 0) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 0.7f, 1.3f);
            }
            if (run.tick < 11) {
                // the dive
                Vec3 to = t != null ? t.getBoundingBox().getCenter().add(0, t.getBbHeight() * 0.4, 0)
                        : user.position().add(AbilityUtil.aim(user).scale(8));
                Vec3 d = to.subtract(user.position().add(0, user.getBbHeight() * 0.3, 0));
                if (d.lengthSqr() > 0.5) {
                    user.setDeltaMovement(d.normalize().scale(1.25));
                    user.hurtMarked = true;
                }
                Vec3 back = user.position().add(0, user.getBbHeight() * 0.5, 0);
                Fx.speedLine(level, back, back.add(d.normalize().scale(-2.0)));
                if (t != null && run.counter == 0 && user.distanceTo(t) < 2.2 + user.getBbWidth()) {
                    run.counter = 1; // caught
                    AbilityUtil.hurtIgnoringIFrames(user, t, 6f);
                    AbilityUtil.blood(level, t.getBoundingBox().getCenter(), 16, 0.2);
                    AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.0f, 0.8f);
                }
                return;
            }
            if (run.tick < 28) {
                // haul it up
                user.setDeltaMovement(user.getDeltaMovement().multiply(0.5, 0, 0.5).add(0, 0.42, 0));
                user.hurtMarked = true;
                if (run.tick % 4 == 0) {
                    AbilityUtil.sound(user, ModSounds.DEVIL_FLAP.get(), 1.0f, 0.9f);
                }
                if (t != null && run.counter == 1) {
                    Vec3 below = user.position().add(0, -t.getBbHeight() - 0.1, 0);
                    t.teleportTo(below.x, below.y, below.z);
                    t.setDeltaMovement(Vec3.ZERO);
                    t.fallDistance = 0;
                    t.hurtMarked = true;
                }
                return;
            }
            if (run.tick == 28 && t != null && run.counter == 1) {
                // let go
                t.setDeltaMovement(0, -0.6, 0);
                t.hurtMarked = true;
                run.counter = 2;
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 0.9f, 1.1f);
            }
        }
    }

    /** A screech that scrambles everything around it. */
    public static class Screech extends DevilAbility {
        public Screech() {
            super(HybridType.BAT, "bat_screech");
            timing(20, 120);
            cost(6);
            anim("", "screech");
            ai(0, 10, 8);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 c = user.position().add(0, user.getBbHeight() * 0.7, 0);
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 2.0f, 1.0f);
                for (LivingEntity e : AbilityUtil.inRadius(user, c, 10)) {
                    AbilityUtil.hurt(user, e, 6f);
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.CONFUSION, 120, 0)));
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1)));
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 80, 0)));
                }
            }
            if (run.tick >= 4 && run.tick <= 16 && run.tick % 3 == 1) {
                // rings of sound spreading out from its head and along the ground
                Fx.shockwave(level, c, 1.5 + (run.tick - 4) * 0.8, Fx.STEEL_RING);
                Fx.shockwave(level, user.position(), 1.5 + (run.tick - 4) * 0.8, Fx.STEEL_RING);
            }
        }
    }

    private BatMoves() {
    }
}
