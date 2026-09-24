package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.devil.DevilEvents;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.Tags;

import java.util.List;

/**
 * The Chainsaw Devil's true form: Pochita as the Hero of Hell. A huge black armoured devil with a saw out of its head
 * and each forearm split at the elbow into two saws, its guts wound round its neck like a scarf. Devils fear it above
 * everything, because what it eats is erased - it never comes back, in Hell or on Earth.
 * <p>
 * A Chainsaw hybrid becomes it for a while ({@link com.csm.hybrids.ability.chainsaw.ChainsawAbilities.HeroOfHell});
 * it is also fought as a mob.
 */
public final class HeroMoves {
    /** Set on a devil the Chainsaw Devil has eaten: nothing brings it back (the Tomato Devil's seeds included). */
    public static final String ERASED = "csm_erased";

    public static List<Ability> chainsawDevil() {
        return List.of(new Rend(), new RevCharge(), new ChainWhip(), new Devour(), new Roar());
    }

    private static Vec3 flat(Vec3 v) {
        Vec3 f = new Vec3(v.x, 0, v.z);
        return f.lengthSqr() < 1e-4 ? new Vec3(0, 0, 1) : f.normalize();
    }

    /** Four saws - two out of each split forearm - tear through everything in front of it. */
    public static class Rend extends DevilAbility {
        public Rend() {
            super(HybridType.CHAINSAW_DEVIL, "hero_rend");
            timing(20, 30);
            anim("", "rend");
            revs();
            ai(0, 4, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick == 0) {
                AbilityUtil.sound(user, ModSounds.CHAINSAW_REV.get(), 1.6f, 0.75f);
            }
            if (run.tick != 4 && run.tick != 8 && run.tick != 12 && run.tick != 16) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 eye = user.getEyePosition().add(0, -user.getBbHeight() * 0.2, 0);
            boolean any = false;
            for (LivingEntity e : coneTargets(user, run, eye, aim, 4.5 + user.getBbWidth() * 0.5, 70)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 11f);
                AbilityUtil.push(e, user.position(), 0.4, 0.15);
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 34, 0.35);
                Fx.bloodSpray(level, c, aim, 16, 0.5);
                Fx.sparks(level, c, aim.scale(-1), 8, 0.45);
                any = true;
            }
            Vec3 sweep = eye.add(aim.scale(2.0 + user.getBbWidth() * 0.4));
            Vec3 side = AbilityUtil.right(user).scale(run.tick % 8 == 4 ? 1 : -1);
            Fx.slash(level, sweep, side.add(0, run.tick < 10 ? -0.4 : 0.4, 0), 2.8);
            AbilityUtil.sound(user, any ? ModSounds.CHAINSAW_CUT.get() : ModSounds.CHAINSAW_REV.get(), 1.3f,
                    0.8f + run.tick * 0.02f);
        }
    }

    /** Head down, the saw on its head screaming: it runs through everything in its way. */
    public static class RevCharge extends DevilAbility {
        public RevCharge() {
            super(HybridType.CHAINSAW_DEVIL, "hero_charge");
            timing(22, 80);
            cost(4);
            anim("", "charge");
            revs();
            mobile();
            ai(4, 16, 9);
            reach(20);
        }

        @Override
        public void begin(LivingEntity user, AbilityRun run) {
            super.begin(user, run);
            LivingEntity t = target(run);
            run.vec = t != null ? flat(t.position().subtract(user.position())) : flat(AbilityUtil.aim(user));
            AbilityUtil.sound(user, ModSounds.CHAINSAW_REV.get(), 1.8f, 0.7f);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick < 3 || run.tick > 18 || run.vec == null) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 v = run.vec.scale(1.45);
            user.setDeltaMovement(v.x, Math.min(user.getDeltaMovement().y, 0.05), v.z);
            user.hurtMarked = true;
            user.fallDistance = 0;
            Vec3 tip = user.getEyePosition().add(run.vec.scale(1.2 + user.getBbWidth() * 0.6));
            Fx.sparks(level, tip, run.vec, 6, 0.4);
            if (run.tick % 2 == 0) {
                Vec3 mid = user.position().add(0, user.getBbHeight() * 0.5, 0);
                Fx.speedLine(level, mid.add(run.vec.scale(0.5)), mid.subtract(run.vec.scale(3.0)));
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, tip.add(0, -0.6, 0), 1.6 + user.getBbWidth() * 0.4)) {
                if (run.hit.add(e.getId())) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 18f);
                    AbilityUtil.push(e, user.position(), 1.6, 0.5);
                    Vec3 c = e.getBoundingBox().getCenter();
                    AbilityUtil.blood(level, c, 50, 0.45);
                    Fx.impact(level, c, 2.0);
                    AbilityUtil.sound(user, ModSounds.CHAINSAW_CUT.get(), 1.4f, 0.8f);
                }
            }
        }
    }

    /** The chains come off its saws and whip round it in a wide circle, then drag everything they caught to its feet. */
    public static class ChainWhip extends DevilAbility {
        public ChainWhip() {
            super(HybridType.CHAINSAW_DEVIL, "hero_chains");
            timing(26, 140);
            cost(6);
            anim("", "chains");
            ai(3, 9, 8);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 c = user.position().add(0, user.getBbHeight() * 0.55, 0);
            double r = 8 + user.getBbWidth() * 0.5;
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.CHAIN_THROW.get(), 1.8f, 0.6f);
            }
            if (run.tick >= 6 && run.tick <= 13) {
                // two chains sweeping round in opposite directions
                double a = (run.tick - 6) / 7.0 * Math.PI * 2;
                for (int k = 0; k < 2; k++) {
                    double b = k == 0 ? a : -a + Math.PI;
                    Vec3 end = c.add(Math.cos(b) * r, -0.6, Math.sin(b) * r);
                    Fx.chain(level, c, end, 6);
                }
                for (LivingEntity e : AbilityUtil.inRadius(user, c, r)) {
                    if (run.hit.add(e.getId())) {
                        AbilityUtil.hurtIgnoringIFrames(user, e, 9f);
                        AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 16, 0.3);
                        AbilityUtil.sound(user, ModSounds.CHAIN_HIT.get(), 1.2f, 0.8f);
                    }
                }
            }
            if (run.tick == 17) {
                AbilityUtil.sound(user, ModSounds.CONTROL_CHAIN.get(), 1.6f, 0.7f);
                for (int id : run.hit) {
                    if (level.getEntity(id) instanceof LivingEntity e && e.isAlive()) {
                        Vec3 pull = user.position().subtract(e.position());
                        double d = pull.length();
                        if (d > 1e-3) {
                            Vec3 v = pull.normalize().scale(Math.min(2.2, d * 0.28));
                            e.setDeltaMovement(v.x, 0.35, v.z);
                            e.hurtMarked = true;
                            Fx.chain(level, c, e.getBoundingBox().getCenter(), 8);
                        }
                    }
                }
            }
        }
    }

    /**
     * It seizes its prey and eats it. A devil it eats is erased - gone from Hell and Earth for good. Anything weak enough
     * is eaten outright; the rest lose a great bite of themselves, which heals it.
     */
    public static class Devour extends DevilAbility {
        public Devour() {
            super(HybridType.CHAINSAW_DEVIL, "hero_devour");
            timing(28, 240);
            cost(10);
            anim("", "devour");
            ai(0, 3, 7);
            reach(6);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                LivingEntity t = target(run);
                if (t == null || t.distanceTo(user) > reach + t.getBbWidth() || !AbilityUtil.canHit(user, t)) {
                    t = null;
                    for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                            3.5 + user.getBbWidth() * 0.5, 50)) {
                        t = e;
                        break;
                    }
                }
                run.target = t;
                AbilityUtil.sound(user, ModSounds.DEVIL_GROWL.get(), 1.6f, 0.6f);
            }
            LivingEntity t = target(run);
            if (t == null) {
                return;
            }
            boolean movable = !t.getType().is(Tags.EntityTypes.BOSSES) && t.getBbWidth() < 3f;
            if (run.tick > 6 && run.tick < 22 && movable) {
                // held up to its mouth
                Vec3 mouth = user.position().add(flat(AbilityUtil.aim(user)).scale(user.getBbWidth() * 0.5 + 0.6))
                        .add(0, user.getBbHeight() * 0.62 - t.getBbHeight() * 0.5, 0);
                t.setDeltaMovement(mouth.subtract(t.position()).scale(0.5));
                t.fallDistance = 0;
                t.hurtMarked = true;
            }
            if (run.tick == 12 || run.tick == 17) {
                AbilityUtil.hurtIgnoringIFrames(user, t, 8f);
                AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.8f, 0.6f);
                AbilityUtil.blood(level, t.getEyePosition(), 40, 0.4);
            }
            if (run.tick == 22) {
                Vec3 c = t.getBoundingBox().getCenter();
                boolean devil = t instanceof DevilEntity;
                boolean eaten = !(t instanceof Player) && movable
                        && (t.getHealth() <= t.getMaxHealth() * (devil ? 0.4f : 0.3f) || t.getMaxHealth() <= 30f);
                if (eaten) {
                    if (devil) {
                        t.getPersistentData().putBoolean(ERASED, true);
                        t.getPersistentData().putBoolean(DevilEvents.REBORN, true);
                        if (user instanceof Player p) {
                            p.displayClientMessage(Component.translatable("msg.csm.erased", t.getDisplayName())
                                    .withStyle(ChatFormatting.DARK_RED), true);
                        }
                    }
                    t.invulnerableTime = 0;
                    t.hurt(AbilityUtil.source(user), Float.MAX_VALUE);
                    if (t.isAlive()) {
                        t.kill();
                    }
                    user.heal(AbilityUtil.dmg(user, 10f));
                    AbilityUtil.blood(level, c, 140, 0.7);
                    Fx.gore(level, c, 8);
                    AbilityUtil.sound(user, ModSounds.HEART_RIP.get(), 1.8f, 0.6f);
                } else {
                    AbilityUtil.hurtIgnoringIFrames(user, t, 22f);
                    user.heal(AbilityUtil.dmg(user, 6f));
                    AbilityUtil.blood(level, c, 70, 0.5);
                    Fx.gore(level, c, 3);
                    AbilityUtil.push(t, user.position(), 1.2, 0.3);
                }
                Fx.impact(level, c, 2.2);
            }
        }
    }

    /** The roar of the Hero of Hell. Everything that hears it remembers what it is afraid of - devils most of all. */
    public static class Roar extends DevilAbility {
        public Roar() {
            super(HybridType.CHAINSAW_DEVIL, "hero_roar");
            timing(30, 400);
            cost(8);
            anim("", "roar");
            revs();
            ai(0, 14, 5);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 head = user.getEyePosition();
            if (run.tick == 6) {
                AbilityUtil.sound(user, ModSounds.DEVIL_ROAR.get(), 3.0f, 0.5f);
                AbilityUtil.sound(user, ModSounds.CHAINSAW_REV.get(), 2.0f, 0.5f);
            }
            if (run.tick >= 8 && run.tick <= 20 && run.tick % 4 == 0) {
                Fx.shockwave(level, user.position(), 4.0 + (run.tick - 8) * 1.2, Fx.BLOOD_RING);
                Fx.exhaust(level, head.add(0, 0.4, 0), 6);
            }
            if (run.tick != 10) {
                return;
            }
            Fx.impact(level, head.add(AbilityUtil.aim(user).scale(1.5)), 3.0);
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position(), 18)) {
                boolean devil = e instanceof DevilEntity;
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 160, devil ? 2 : 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 120, devil ? 2 : 1)));
                if (e instanceof Player) {
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 80, 0)));
                }
                if (devil || e.distanceTo(user) < 8) {
                    // devils fear the Chainsaw Man above everything: they break off and back away
                    AbilityUtil.push(e, user.position(), devil ? 1.6 : 1.0, 0.35);
                    if (e instanceof Mob m && m.getTarget() == user && !(e instanceof DevilEntity d && d.spec().boss)) {
                        m.setTarget(null);
                    }
                }
                Fx.stars(level, e.getEyePosition().add(0, 0.4, 0), 3, 0.2);
            }
        }
    }

    private HeroMoves() {
    }
}
