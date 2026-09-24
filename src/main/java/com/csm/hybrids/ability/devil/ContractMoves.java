package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModEffects;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/** The devils Public Safety's hunters make contracts with: the Fox, the Curse, the Future and the Ghost. */
public final class ContractMoves {
    public static final String CURSE_STACKS = "csm_curse_stacks";
    public static final String CURSE_UNTIL = "csm_curse_until";
    public static final String FORESIGHT_UNTIL = "csm_foresight_until";
    public static final String FORESIGHT_CHARGES = "csm_foresight_charges";
    public static final String DOOM_AT = "csm_doom_at";
    public static final String DOOM_BY = "csm_doom_by";
    public static final String INTANGIBLE_UNTIL = "csm_intangible_until";

    public static List<Ability> fox() {
        return List.of(new Kon(), new FoxClaw(), new Pounce(), new Devour());
    }

    public static List<Ability> curse() {
        return List.of(new Nail(), new CrushingGrip(), new Hex(), new GraveHands());
    }

    public static List<Ability> future() {
        return List.of(new Foresight(), new Glimpse(), new LongReach(), new FuturesTheBest());
    }

    public static List<Ability> ghost() {
        return List.of(new Strangle(), new Snatch(), new Intangible(), new SenseFear());
    }

    /** Holds {@code e} hanging in the air at {@code at} (a grip, a noose). */
    static void holdAt(LivingEntity e, Vec3 at) {
        Vec3 d = at.subtract(e.position());
        e.setDeltaMovement(d.scale(0.35));
        e.fallDistance = 0;
        e.hurtMarked = true;
    }

    // ================================================================== Fox Devil
    /** "Kon!" - the fox's head lunges from nowhere and bites whatever the hand sign points at clean through. */
    public static class Kon extends DevilAbility {
        public Kon() {
            super(HybridType.FOX, "fox_kon");
            timing(20, 120);
            cost(10);
            anim("", "kon");
            ai(0, 7, 12);
            reach(9);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            LivingEntity t = target(run);
            Vec3 aim = t != null ? t.getBoundingBox().getCenter().subtract(user.getEyePosition()).normalize()
                    : AbilityUtil.aim(user);
            if (run.tick == 5) {
                double reachTo = t != null ? Math.max(0, user.distanceTo(t) - user.getBbWidth() * 0.5 - 1.2) : 3.0;
                double v = Math.min(1.3, reachTo * 0.3);
                user.setDeltaMovement(aim.x * v, 0.15, aim.z * v);
                user.hurtMarked = true;
                AbilityUtil.sound(user, ModSounds.DEVIL_GROWL.get(), 1.4f, 1.3f);
            }
            if (run.tick < 8 || run.tick > 11 || run.counter != 0) {
                return;
            }
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 3.6 + user.getBbWidth() * 0.5, 60)) {
                run.counter = 1;
                AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.6f, 0.8f);
                user.setDeltaMovement(user.getDeltaMovement().scale(0.2));
                AbilityUtil.hurtIgnoringIFrames(user, e, 22f);
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 60, 0.4);
                Fx.bloodSpray(level, c, aim, 24, 0.5);
                Fx.gore(level, c, 3);
                break;
            }
        }
    }

    /** A swipe of the eye-covered forepaw. */
    public static class FoxClaw extends DevilAbility {
        public FoxClaw() {
            super(HybridType.FOX, "fox_claw");
            timing(18, 30);
            cost(0);
            anim("", "claw");
            ai(0, 3, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 1.0f, 1.4f);
            Vec3 c = user.getEyePosition().add(aim.scale(2.0));
            Fx.slash(level, c, aim.cross(new Vec3(0, 1, 0)).add(0, -0.7, 0), 2.2);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 3.4 + user.getBbWidth() * 0.5, 55)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 12f);
                AbilityUtil.push(e, user.position(), 0.9, 0.3);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 24, 0.3);
            }
        }
    }

    /** It springs at its prey from far off and comes down on it with all its weight. */
    public static class Pounce extends DevilAbility {
        public Pounce() {
            super(HybridType.FOX, "fox_pounce");
            timing(28, 100);
            cost(8);
            anim("", "pounce");
            ai(5, 16, 9);
            mobile();
            reach(20);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                LivingEntity t = target(run);
                Vec3 to = t != null ? t.position().subtract(user.position()) : AbilityUtil.aim(user).scale(10);
                Vec3 flat = new Vec3(to.x, 0, to.z);
                double dist = Math.min(16, flat.length());
                Vec3 dir = flat.lengthSqr() > 1e-4 ? flat.normalize() : AbilityUtil.aim(user);
                user.setDeltaMovement(dir.x * dist * 0.11, 0.75, dir.z * dist * 0.11);
                user.hurtMarked = true;
                AbilityUtil.sound(user, ModSounds.DEVIL_GROWL.get(), 1.4f, 1.1f);
                Fx.clods(level, user.position(), 10, 0.3);
            }
            if (run.tick > 6 && run.tick < 26) {
                user.fallDistance = 0;
            }
            if (run.tick > 12 && run.counter == 0 && (user.onGround() || run.tick == 25)) {
                run.counter = 1;
                Vec3 p = user.position();
                AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 1.5f, 0.8f);
                Fx.shockwave(level, p, 4, Fx.BLOOD_RING);
                Fx.clods(level, p, 24, 0.5);
                for (LivingEntity e : AbilityUtil.inRadius(user, p, 3.2 + user.getBbWidth() * 0.5)) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 14f);
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 3)));
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.4);
                }
            }
        }
    }

    /** It catches its prey in its jaws and shakes it like a rabbit, then flings the rest away. */
    public static class Devour extends DevilAbility {
        public Devour() {
            super(HybridType.FOX, "fox_devour");
            timing(30, 160);
            cost(12);
            anim("", "devour");
            ai(0, 3, 8);
            reach(5);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 mouth = user.getEyePosition().add(aim.scale(1.2 + user.getBbWidth() * 0.5)).add(0, -0.4, 0);
            if (run.tick == 4) {
                for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 3.2 + user.getBbWidth() * 0.5,
                        55)) {
                    run.target = e;
                    run.counter = 1;
                    AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.4f, 0.9f);
                    break;
                }
            }
            LivingEntity t = target(run);
            if (run.counter != 1 || t == null) {
                return;
            }
            if (run.tick < 26) {
                double shake = Math.sin(run.tick * 1.6) * 0.8;
                holdAt(t, mouth.add(AbilityUtil.right(user).scale(shake)).subtract(0, t.getBbHeight() * 0.5, 0));
                if (run.tick % 5 == 0) {
                    AbilityUtil.hurtIgnoringIFrames(user, t, 5f);
                    AbilityUtil.blood(level, t.getBoundingBox().getCenter(), 20, 0.4);
                    user.heal(AbilityUtil.dmg(user, 2f));
                }
            } else if (run.tick == 26) {
                AbilityUtil.push(t, user.position(), 1.8, 0.6);
                AbilityUtil.hurtIgnoringIFrames(user, t, 6f);
                Fx.gore(level, t.getBoundingBox().getCenter(), 2);
            }
        }
    }

    // ================================================================== Curse Devil
    /** Stab the same thing three times with the nail and the Curse Devil takes it. */
    public static class Nail extends DevilAbility {
        public Nail() {
            super(HybridType.CURSE, "curse_nail");
            timing(14, 16);
            cost(2);
            anim("", "nail");
            ai(0, 3, 16);
            reach(5);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 6) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 3.4 + user.getBbWidth() * 0.5, 60)) {
                AbilityUtil.sound(user, ModSounds.SPEAR_IMPACT.get(), 1.0f, 1.6f);
                AbilityUtil.hurtIgnoringIFrames(user, e, 5f);
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 12, 0.2);
                CompoundTag tag = e.getPersistentData();
                int stacks = tag.getLong(CURSE_UNTIL) > level.getGameTime() ? tag.getInt(CURSE_STACKS) : 0;
                stacks++;
                tag.putLong(CURSE_UNTIL, level.getGameTime() + 600);
                Fx.shards(level, c, 6 * stacks, 0.2);
                if (stacks >= 3) {
                    tag.putInt(CURSE_STACKS, 0);
                    tag.putLong(CURSE_UNTIL, 0);
                    curseTakes(user, e, level);
                } else {
                    tag.putInt(CURSE_STACKS, stacks);
                    AbilityUtil.sound(user, ModSounds.DEVIL_GROWL.get(), 0.6f + stacks * 0.3f, 0.5f);
                }
                break;
            }
        }

        /** The third nail: the Curse closes its hand around the victim and wrings it. */
        static void curseTakes(LivingEntity user, LivingEntity e, ServerLevel level) {
            AbilityUtil.sound(user, ModSounds.CONTROL_CRUSH.get(), 2.0f, 0.6f);
            AbilityUtil.sound(user, ModSounds.DEVIL_ROAR.get(), 1.6f, 0.5f);
            float dmg = Math.max(40f, e.getMaxHealth() * 0.35f);
            AbilityUtil.hurtIgnoringIFrames(user, e, dmg);
            Vec3 c = e.getBoundingBox().getCenter();
            AbilityUtil.blood(level, c, 120, 0.6);
            Fx.gore(level, c, 6);
            Fx.impact(level, c, 2.4);
            e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 3)));
            e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 200, 1)));
        }
    }

    /** A hand bigger than a man reaches out, closes round its prey, lifts it and wrings it. */
    public static class CrushingGrip extends DevilAbility {
        public CrushingGrip() {
            super(HybridType.CURSE, "curse_grip");
            timing(44, 160);
            cost(14);
            anim("", "grip");
            ai(0, 9, 9);
            reach(12);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            if (run.tick == 8) {
                for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 9 + user.getBbWidth() * 0.5,
                        25)) {
                    run.target = e;
                    run.counter = 1;
                    AbilityUtil.sound(user, ModSounds.CONTROL_CRUSH.get(), 1.2f, 0.7f);
                    break;
                }
            }
            LivingEntity t = target(run);
            if (run.counter != 1 || t == null) {
                return;
            }
            Vec3 grip = user.getEyePosition().add(aim.scale(3.0 + user.getBbWidth() * 0.5)).add(0, 1.0, 0);
            if (run.tick < 36) {
                holdAt(t, grip.subtract(0, t.getBbHeight() * 0.5, 0));
                if (run.tick % 6 == 0) {
                    AbilityUtil.hurtIgnoringIFrames(user, t, 4f);
                    AbilityUtil.blood(level, t.getBoundingBox().getCenter(), 16, 0.3);
                    AbilityUtil.sound(user, ModSounds.CONTROL_CRUSH.get(), 0.8f, 1.2f);
                }
            } else if (run.tick == 36) {
                t.setDeltaMovement(0, -2.2, 0);
                t.hurtMarked = true;
                AbilityUtil.hurtIgnoringIFrames(user, t, 10f);
                Fx.impact(level, t.position(), 1.6);
                Fx.clods(level, t.position(), 20, 0.4);
                AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 1.5f, 0.7f);
            }
        }
    }

    /** A curse on everything in front of it: sapped, slowed, and its wounds won't close. */
    public static class Hex extends DevilAbility {
        public Hex() {
            super(HybridType.CURSE, "curse_hex");
            timing(30, 240);
            cost(12);
            anim("", "hex");
            ai(0, 12, 7);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 1.6f, 0.4f);
            }
            if (run.tick < 10 || run.tick > 20 || run.tick % 2 != 0) {
                return;
            }
            Vec3 aim = AbilityUtil.aim(user);
            double r = 2 + (run.tick - 10) * 1.1;
            Vec3 p = user.getEyePosition().add(aim.scale(r));
            Fx.smoke(level, p, 10, 1.0 + r * 0.15);
            Fx.shards(level, p, 6, 0.1);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 13, 40)) {
                if (!run.hit.add(e.getId())) {
                    continue;
                }
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(ModEffects.UNHEALING.get(), 240, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 240, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 240, 1)));
                AbilityUtil.hurtIgnoringIFrames(user, e, 6f);
                CompoundTag tag = e.getPersistentData();
                int stacks = tag.getLong(CURSE_UNTIL) > level.getGameTime() ? tag.getInt(CURSE_STACKS) : 0;
                tag.putInt(CURSE_STACKS, Math.min(2, stacks + 1));
                tag.putLong(CURSE_UNTIL, level.getGameTime() + 600);
            }
        }
    }

    /** Bony hands claw up out of the ground all round it and drag everything down. */
    public static class GraveHands extends DevilAbility {
        public GraveHands() {
            super(HybridType.CURSE, "curse_rise");
            timing(40, 280);
            cost(16);
            anim("", "rise");
            fx("rise");
            ai(0, 8, 7);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 10) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 1.8f, 0.5f);
                Fx.shockwave(level, user.position(), 9, Fx.STEEL_RING);
            }
            if (run.tick < 12 || run.tick > 36) {
                return;
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position(), 9)) {
                if (!e.onGround() && e.getY() > user.getY() + 3) {
                    continue;
                }
                e.setDeltaMovement(e.getDeltaMovement().multiply(0.1, 1, 0.1).add(0, -0.3, 0));
                e.hurtMarked = true;
                if (run.hit.add(e.getId())) {
                    Fx.clods(level, e.position(), 14, 0.35);
                    AbilityUtil.hurtIgnoringIFrames(user, e, 10f);
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 5)));
                    AbilityUtil.blood(level, e.position().add(0, 0.5, 0), 16, 0.3);
                } else if (run.tick % 8 == 0) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 3f);
                }
            }
        }
    }

    // ================================================================== Future Devil
    /** It sees what is coming: the next few blows aimed at it simply miss. */
    public static class Foresight extends DevilAbility {
        public Foresight() {
            super(HybridType.FUTURE, "future_foresight");
            timing(16, 300);
            cost(12);
            anim("", "foresight");
            ai(0, 20, 10);
            blind();
        }

        @Override
        public boolean aiReady(DevilEntity mob, LivingEntity target) {
            return mob.getPersistentData().getLong(FORESIGHT_UNTIL) < mob.level().getGameTime();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 6) {
                return;
            }
            ServerLevel level = level(user);
            CompoundTag tag = user.getPersistentData();
            tag.putLong(FORESIGHT_UNTIL, level.getGameTime() + 300);
            tag.putInt(FORESIGHT_CHARGES, 5);
            AbilityUtil.sound(user, ModSounds.COSMOS_HALLOWEEN.get(), 0.8f, 1.6f);
            Fx.stars(level, user.getEyePosition(), 16, 0.6);
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position(), 24)) {
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.GLOWING, 300, 0)));
            }
        }
    }

    /** It shows its prey how it will die - and a moment later it does, a little. */
    public static class Glimpse extends DevilAbility {
        public Glimpse() {
            super(HybridType.FUTURE, "future_glimpse");
            timing(24, 200);
            cost(14);
            anim("", "glimpse");
            ai(0, 18, 9);
            reach(24);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 12) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 20, 12)) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 1.0f, 1.4f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 120, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 2)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 160, 1)));
                CompoundTag tag = e.getPersistentData();
                tag.putLong(DOOM_AT, level.getGameTime() + 60);
                tag.putUUID(DOOM_BY, user.getUUID());
                tag.putFloat("csm_doom_dmg", AbilityUtil.dmg(user, 16f));
                Fx.stars(level, e.getEyePosition(), 10, 0.4);
                break;
            }
        }
    }

    /** Its long, many-jointed arms reach out of its hollow and swat. */
    public static class LongReach extends DevilAbility {
        public LongReach() {
            super(HybridType.FUTURE, "future_reach");
            timing(18, 30);
            cost(0);
            anim("", "reach");
            ai(0, 6, 14);
            reach(9);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 9) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 1.0f, 1.2f);
            Fx.slash(level, user.getEyePosition().add(aim.scale(3.5)), aim.cross(new Vec3(0, 1, 0)), 3.0);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 6 + user.getBbWidth() * 0.5, 40)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 11f);
                AbilityUtil.push(e, user.position(), 1.2, 0.35);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 20, 0.3);
            }
        }
    }

    /** "Future's the best! Future's the best!" - it dances, and the future looks bright for its side. */
    public static class FuturesTheBest extends DevilAbility {
        public FuturesTheBest() {
            super(HybridType.FUTURE, "future_best");
            timing(50, 400);
            cost(10);
            anim("", "dance");
            ai(0, 30, 5);
            blind();
        }

        @Override
        public boolean aiReady(DevilEntity mob, LivingEntity target) {
            return mob.getHealth() < mob.getMaxHealth() * 0.7f;
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick % 12 == 0) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 0.8f, 1.8f);
                Fx.stars(level, user.getEyePosition().add(0, 0.5, 0), 8, 0.8);
            }
            if (run.tick != 40) {
                return;
            }
            user.heal(user.getMaxHealth() * 0.2f);
            user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 400, 1)));
            user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 400, 0)));
            if (user instanceof ServerPlayer) {
                user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 400, 1)));
                user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.LUCK, 1200, 2)));
            }
            Fx.shockwave(level, user.position(), 6, Fx.STEEL_RING);
        }
    }

    // ================================================================== Ghost Devil
    /** Hands no one can see close round a throat and lift. */
    public static class Strangle extends DevilAbility {
        public Strangle() {
            super(HybridType.GHOST, "ghost_strangle");
            timing(50, 160);
            cost(12);
            anim("", "strangle");
            ai(0, 14, 11);
            reach(20);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user), 16, 14)) {
                    run.target = e;
                    run.counter = 1;
                    run.vec = e.position().add(0, 1.8, 0);
                    AbilityUtil.sound(user, ModSounds.CONTROL_CRUSH.get(), 0.8f, 1.5f);
                    break;
                }
            }
            LivingEntity t = target(run);
            if (run.counter != 1 || t == null || run.tick > 44) {
                return;
            }
            holdAt(t, run.vec);
            t.setAirSupply(Math.max(-10, t.getAirSupply() - 20));
            t.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 20, 4)));
            if (run.tick % 8 == 0) {
                AbilityUtil.hurtIgnoringIFrames(user, t, 4f);
                Fx.smoke(level, t.getEyePosition(), 4, 0.2);
            }
        }
    }

    /** An unseen hand snatches its prey up and throws it. */
    public static class Snatch extends DevilAbility {
        public Snatch() {
            super(HybridType.GHOST, "ghost_snatch");
            timing(24, 80);
            cost(6);
            anim("", "snatch");
            ai(0, 12, 12);
            reach(16);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user), 13, 16)) {
                    run.target = e;
                    run.counter = 1;
                    break;
                }
            }
            LivingEntity t = target(run);
            if (run.counter != 1 || t == null) {
                return;
            }
            if (run.tick < 14) {
                holdAt(t, t.position().add(0, 0.6, 0));
            } else if (run.tick == 14) {
                Vec3 away = t.position().subtract(user.position());
                Vec3 flat = new Vec3(away.x, 0, away.z).normalize();
                Vec3 side = AbilityUtil.right(user).scale(level.random.nextBoolean() ? 1 : -1);
                Vec3 fling = flat.scale(-0.4).add(side).normalize().scale(1.6);
                t.setDeltaMovement(fling.x, 0.9, fling.z);
                t.hurtMarked = true;
                AbilityUtil.hurtIgnoringIFrames(user, t, 10f);
                AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 1.2f, 1.4f);
                Fx.smoke(level, t.getBoundingBox().getCenter(), 10, 0.5);
            }
        }
    }

    /** It is a ghost: for a while nothing can touch it. */
    public static class Intangible extends DevilAbility {
        public Intangible() {
            super(HybridType.GHOST, "ghost_intangible");
            timing(10, 360);
            cost(14);
            anim("", "fade");
            ai(0, 30, 8);
            blind();
        }

        @Override
        public boolean aiReady(DevilEntity mob, LivingEntity target) {
            return mob.getHealth() < mob.getMaxHealth() * 0.6f;
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            ServerLevel level = level(user);
            user.getPersistentData().putLong(INTANGIBLE_UNTIL, level.getGameTime() + 120);
            user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.INVISIBILITY, 120, 0, false, false)));
            user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 120, 1, false, false)));
            AbilityUtil.sound(user, ModSounds.COSMOS_VOID.get(), 0.8f, 1.6f);
            Fx.smoke(level, user.getBoundingBox().getCenter(), 30, 1.0);
        }
    }

    /** It can smell fear: everything afraid nearby shows itself, and shakes. */
    public static class SenseFear extends DevilAbility {
        public SenseFear() {
            super(HybridType.GHOST, "ghost_fear");
            timing(24, 300);
            cost(8);
            anim("", "fear");
            ai(0, 20, 6);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 12) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 1.4f, 0.6f);
            Fx.shockwave(level, user.position(), 20, Fx.STEEL_RING);
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position(), 20)) {
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.GLOWING, 300, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 200, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 200, 1)));
                if (e.getHealth() < e.getMaxHealth() * 0.5f) {
                    // the frightened freeze
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 3)));
                    Fx.smoke(level, e.getEyePosition(), 6, 0.3);
                }
            }
        }
    }

    private ContractMoves() {
    }
}
