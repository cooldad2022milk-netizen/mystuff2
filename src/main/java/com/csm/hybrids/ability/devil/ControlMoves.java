package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
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
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * Makima, the Control Devil. She dominates anyone she deems beneath her; an unseen force crushes the targets she names
 * from afar (her finger-gun "Bang"); chains bind the ones she has not yet tamed; and the Prime Minister's contract
 * turns the injuries meant for her onto someone else.
 */
public final class ControlMoves {
    public static final String CONTRACT_UNTIL = "csm_contract_until";
    public static final String THRALL_UNTIL = "csm_thrall_until";

    public static List<Ability> all() {
        return List.of(new Bang(), new Chains(), new Domination(), new Kneel(), new PrimeMinister());
    }

    /** Players only get her full strength while the Control Devil is out (slot 0). */
    static float power(LivingEntity user) {
        if (user instanceof Player p) {
            HybridData d = HybridCapability.get(p);
            return d != null && d.isTransformed() ? 1f : 0.6f;
        }
        return 1f;
    }

    /** An unseen force folds the target in on itself where it stands. */
    static void crush(LivingEntity user, LivingEntity t, float amount) {
        ServerLevel level = (ServerLevel) user.level();
        t.invulnerableTime = 0;
        t.hurt(user.damageSources().indirectMagic(user, user), AbilityUtil.dmg(user, amount));
        t.setDeltaMovement(t.getDeltaMovement().multiply(0.2, 0, 0.2).add(0, -1.2, 0));
        t.hurtMarked = true;
        t.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2)));
        Vec3 c = t.getBoundingBox().getCenter();
        AbilityUtil.blood(level, c, 70, 0.45);
        Fx.bloodSpray(level, c, new Vec3(0, 1, 0), 30, 0.7);
        Fx.impact(level, c, 2.6);
        Fx.shockwave(level, t.position().add(0, 0.05, 0), 2.8, Fx.BLOOD_RING);
        AbilityUtil.soundAt(level, c, ModSounds.CONTROL_CRUSH.get(), 1.6f, 0.9f);
    }

    /** "Bang": she points a finger gun at a target and the target is crushed - from any distance. */
    public static class Bang extends DevilAbility {
        public Bang() {
            super(HybridType.CONTROL, "control_bang");
            anyForm();
            timing(24, 70);
            cost(8);
            anim("control_bang", "bang");
            fx("bang");
            ai(3, 48, 12);
            reach(72);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            LivingEntity t = target(run);
            if (t != null && run.tick < 10 && run.tick % 3 == 0) {
                // the target she has named: the air round it tightens
                Fx.shockwave(level, t.position().add(0, 0.05, 0), 1.2 + 0.1 * run.tick, Fx.BLOOD_RING);
            }
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.CONTROL_BANG.get(), 0.7f, 1.5f);
            }
            if (run.tick != 10) {
                return;
            }
            AbilityUtil.sound(user, ModSounds.CONTROL_BANG.get(), 1.4f, 1.0f);
            Vec3 tip = AbilityUtil.handPos(user, true, 0.9);
            Fx.impact(level, tip, 0.5);
            if (t == null) {
                // nothing named: the force lands wherever she points
                HitResult hit = AbilityUtil.raycastBlock(user, reach);
                Vec3 p = hit.getLocation();
                Fx.impact(level, p, 2.0);
                Fx.shockwave(level, p, 2.4, Fx.STEEL_RING);
                return;
            }
            if (!(user instanceof Player) && !user.hasLineOfSight(t)) {
                return; // the named target got out of her sight in time
            }
            crush(user, t, 26f * power(user));
        }
    }

    /** Chains burst out of the ground and bind whatever stands in front of her, dragging it to her feet. */
    public static class Chains extends DevilAbility {
        public Chains() {
            super(HybridType.CONTROL, "control_chains");
            timing(20, 100);
            cost(10);
            anim("control_chains", "chains");
            fx("chains");
            ai(2, 16, 10);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.CONTROL_CHAIN.get(), 1.4f, 1.0f);
            List<LivingEntity> hit = coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user), 18, 38);
            int n = 0;
            for (LivingEntity e : hit) {
                if (n++ >= 6) {
                    break;
                }
                Vec3 c = e.getBoundingBox().getCenter();
                for (int k = 0; k < 3; k++) {
                    double a = k * Math.PI * 2 / 3 + level.random.nextDouble();
                    Vec3 root = e.position().add(Math.cos(a) * 1.6, 0.05, Math.sin(a) * 1.6);
                    Fx.chain(level, root, c, 30);
                    Fx.clods(level, root, 4, 0.2);
                }
                AbilityUtil.hurt(user, e, 8f * power(user));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 6)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 60, 0)));
                AbilityUtil.push(e, user.position(), -0.8, 0.15);
            }
            if (hit.isEmpty()) {
                // lash the ground ahead anyway
                Vec3 ahead = user.position().add(AbilityUtil.aim(user).multiply(1, 0, 1).normalize().scale(6));
                Fx.chain(level, ahead, ahead.add(0, 2.5, 0), 20);
            }
        }
    }

    /**
     * Domination: every creature around her that is beneath her (anything but a boss or something far stronger) becomes
     * her thrall for a minute and turns on whoever she fights.
     */
    public static class Domination extends DevilAbility {
        public Domination() {
            super(HybridType.CONTROL, "control_domination");
            timing(30, 500);
            cost(20);
            anim("control_domination", "domination");
            fx("domination");
            ai(0, 30, 6);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.CONTROL_DOMINATE.get(), 1.4f, 1.0f);
            }
            if (run.tick != 14) {
                return;
            }
            double r = 24;
            int count = 0;
            float own = user.getMaxHealth();
            for (Mob m : level.getEntitiesOfClass(Mob.class, new AABB(user.position(), user.position()).inflate(r),
                    m -> m != user && m.isAlive() && m.distanceToSqr(user) <= r * r)) {
                if (m instanceof DevilEntity d && (d.spec().boss || d.devilType() == HybridType.CONTROL)) {
                    continue; // she cannot dominate her equals
                }
                if (m.getMaxHealth() > Math.max(own * 3f, 120f)) {
                    continue;
                }
                DevilEntity.enthrall(m, user.getUUID());
                m.getPersistentData().putLong(THRALL_UNTIL, level.getGameTime() + 1200);
                m.setTarget(user instanceof Mob mob ? mob.getTarget() : null);
                Vec3 h = m.getEyePosition().add(0, 0.5, 0);
                Fx.stars(level, h, 6, 0.2);
                Fx.shockwave(level, m.position().add(0, 0.05, 0), 1.0, Fx.BLOOD_RING);
                count++;
            }
            Fx.shockwave(level, user.position().add(0, 0.05, 0), 8.0, Fx.BLOOD_RING);
            if (user instanceof Player p) {
                p.displayClientMessage(Component.translatable("msg.csm.dominated", count).withStyle(ChatFormatting.RED),
                        true);
            }
        }
    }

    /** "Kneel": everyone around her is slammed down to the floor. */
    public static class Kneel extends DevilAbility {
        public Kneel() {
            super(HybridType.CONTROL, "control_kneel");
            timing(16, 160);
            cost(8);
            anim("control_kneel", "kneel");
            ai(0, 8, 9);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 6) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.CONTROL_CRUSH.get(), 1.4f, 0.6f);
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position().add(0, 1, 0), 10)) {
                e.setDeltaMovement(e.getDeltaMovement().multiply(0.1, 0, 0.1).add(0, -1.6, 0));
                e.hurtMarked = true;
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 4)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 80, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.JUMP, 60, 128))); // jump boost 129 = no jumping
                AbilityUtil.hurt(user, e, 6f * power(user));
                Fx.impact(level, e.position().add(0, 0.3, 0), 1.2);
                if (e instanceof Player p) {
                    p.displayClientMessage(Component.translatable("msg.csm.kneel").withStyle(ChatFormatting.DARK_RED), true);
                }
            }
            Fx.shockwave(level, user.position().add(0, 0.05, 0), 10.0, Fx.STEEL_RING);
            Fx.shockwave(level, user.position().add(0, 0.05, 0), 5.0, Fx.BLOOD_RING);
        }
    }

    /** The Prime Minister's contract: for 20 seconds every injury meant for her lands on someone nearby instead. */
    public static class PrimeMinister extends DevilAbility {
        public PrimeMinister() {
            super(HybridType.CONTROL, "control_contract");
            timing(14, 900);
            cost(25);
            anim("control_contract", "contract");
            ai(0, 40, 20);
            blind();
        }

        @Override
        public boolean aiReady(DevilEntity mob, LivingEntity target) {
            return mob.getHealth() < mob.getMaxHealth() * 0.6f;
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 7) {
                return;
            }
            ServerLevel level = level(user);
            user.getPersistentData().putLong(CONTRACT_UNTIL, level.getGameTime() + 400);
            AbilityUtil.sound(user, ModSounds.CONTROL_DOMINATE.get(), 1.2f, 1.4f);
            Fx.stars(level, user.getEyePosition(), 20, 0.5);
            Fx.shockwave(level, user.position().add(0, 0.05, 0), 3.0, Fx.STEEL_RING);
            if (user instanceof Player p) {
                p.displayClientMessage(Component.translatable("msg.csm.contract").withStyle(ChatFormatting.GOLD), true);
            }
        }
    }

    private ControlMoves() {
    }
}
