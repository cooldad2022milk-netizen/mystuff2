package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/** Devils from the second part: the Falling Devil and the Justice Devil. */
public final class PartTwoMoves {

    public static List<Ability> falling() {
        return List.of(new FallUp(), new FirstCourse(), new Plunge());
    }

    public static List<Ability> justice() {
        return List.of(new Gavel(), new TentacleLash(), new BellyJaw());
    }

    // ================================================================== Falling Devil
    /** The fear of falling: everything around it falls - up, into the sky - and comes back down. */
    public static class FallUp extends DevilAbility {
        public FallUp() {
            super(HybridType.FALLING, "falling_fall");
            timing(32, 240);
            cost(14);
            anim("", "fall");
            ai(0, 12, 10);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 2.0f, 0.5f);
            Fx.shockwave(level, user.position(), 10, Fx.STEEL_RING);
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position(), 10)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 4f);
                e.setDeltaMovement(e.getDeltaMovement().multiply(0.2, 0, 0.2).add(0, 1.4, 0));
                e.hurtMarked = true;
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.LEVITATION, 36, 5)));
                Fx.smoke(level, e.position(), 6, 0.4);
            }
        }
    }

    /** "The first course": it serves its prey the fall it fears most, and the prey relives it. */
    public static class FirstCourse extends DevilAbility {
        public FirstCourse() {
            super(HybridType.FALLING, "falling_course");
            timing(28, 200);
            cost(12);
            anim("", "course");
            ai(0, 14, 9);
            reach(16);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 14) {
                return;
            }
            ServerLevel level = level(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user), 14, 20)) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 1.2f, 0.5f);
                AbilityUtil.hurtIgnoringIFrames(user, e, 10f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.CONFUSION, 120, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 2)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 160, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 80, 0)));
                AbilityUtil.blood(level, e.getEyePosition(), 20, 0.3);
                Fx.stars(level, e.getEyePosition(), 8, 0.4);
                break;
            }
        }
    }

    /** It tips over and drops on its prey head first. */
    public static class Plunge extends DevilAbility {
        public Plunge() {
            super(HybridType.FALLING, "falling_plunge");
            timing(24, 140);
            cost(10);
            anim("", "plunge");
            ai(2, 12, 8);
            mobile();
            reach(16);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                LivingEntity t = target(run);
                Vec3 to = t != null ? t.position().subtract(user.position()) : AbilityUtil.aim(user).scale(8);
                Vec3 flat = new Vec3(to.x, 0, to.z);
                double dist = Math.min(12, flat.length());
                Vec3 dir = flat.lengthSqr() > 1e-4 ? flat.normalize() : AbilityUtil.aim(user);
                user.setDeltaMovement(dir.x * dist * 0.12, 0.9, dir.z * dist * 0.12);
                user.hurtMarked = true;
                AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 1.4f, 0.8f);
            }
            if (run.tick > 6 && run.tick < 24) {
                user.fallDistance = 0;
            }
            if (run.tick > 12 && run.counter == 0 && (user.onGround() || run.tick == 22)) {
                run.counter = 1;
                Vec3 p = user.position();
                AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 2.0f, 0.6f);
                Fx.shockwave(level, p, 4.5, Fx.BLOOD_RING);
                Fx.clods(level, p, 30, 0.5);
                for (LivingEntity e : AbilityUtil.inRadius(user, p, 3.5 + user.getBbWidth() * 0.5)) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 16f);
                    AbilityUtil.push(e, p, 1.0, 0.5);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.4);
                }
            }
        }
    }

    // ================================================================== Justice Devil
    /** The arm that became a gavel comes down: the sentence is carried out. */
    public static class Gavel extends DevilAbility {
        public Gavel() {
            super(HybridType.JUSTICE, "justice_gavel");
            timing(24, 60);
            cost(8);
            anim("", "gavel");
            ai(0, 5, 12);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 11) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 at = user.position().add(new Vec3(aim.x, 0, aim.z).normalize().scale(2.0 + user.getBbWidth() * 0.5));
            AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 2.0f, 0.7f);
            Fx.shockwave(level, at, 3.5, Fx.STEEL_RING);
            Fx.impact(level, at.add(0, 0.5, 0), 2.0);
            Fx.clods(level, at, 24, 0.5);
            for (LivingEntity e : AbilityUtil.inRadius(user, at.add(0, 0.8, 0), 3.2)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 16f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3)));
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.4);
            }
        }
    }

    /** The tentacles it can't control whip out all round it. */
    public static class TentacleLash extends DevilAbility {
        public TentacleLash() {
            super(HybridType.JUSTICE, "justice_lash");
            timing(20, 100);
            cost(8);
            anim("", "lash");
            ai(0, 6, 10);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick < 6 || run.tick > 12 || run.tick % 2 != 0) {
                return;
            }
            ServerLevel level = level(user);
            if (run.tick == 6) {
                AbilityUtil.sound(user, ModSounds.WHIP_LASH.get(), 1.6f, 0.6f);
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position().add(0, 1, 0), 6 + user.getBbWidth() * 0.5)) {
                if (!run.hit.add(e.getId())) {
                    continue;
                }
                AbilityUtil.hurtIgnoringIFrames(user, e, 10f);
                AbilityUtil.push(e, user.position(), 1.2, 0.4);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 18, 0.3);
            }
        }
    }

    /** Its belly splits open into an enormous jaw and bites down on whatever is in front of it. */
    public static class BellyJaw extends DevilAbility {
        public BellyJaw() {
            super(HybridType.JUSTICE, "justice_jaw");
            timing(22, 140);
            cost(10);
            anim("", "jaw");
            ai(0, 4, 9);
            reach(6);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 10) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 2.0f, 0.5f);
            for (LivingEntity e : coneTargets(user, run, user.position().add(0, user.getBbHeight() * 0.5, 0),
                    AbilityUtil.aim(user), 4 + user.getBbWidth() * 0.5, 60)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 18f);
                user.heal(AbilityUtil.dmg(user, 4f));
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 50, 0.45);
                Fx.gore(level, c, 3);
            }
        }
    }

    private PartTwoMoves() {
    }
}
