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
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * The Leech Devil: a faceless mouth on a creased four-legged bulk. It stabs with a long tongue, grabs with sucker-lined
 * tentacles, bites with its enormous maw, and drinks its prey dry.
 */
public final class LeechMoves {

    public static List<Ability> all() {
        return List.of(new Tongue(), new Grab(), new Devour(), new Drain());
    }

    static Vec3 maw(LivingEntity user) {
        return user.position().add(0, user.getBbHeight() * 0.55, 0).add(AbilityUtil.aim(user).multiply(1, 0, 1)
                .normalize().scale(user.getBbWidth() * 0.55));
    }

    static void drink(LivingEntity user, float amount) {
        user.heal(amount);
        if (user instanceof ServerPlayer sp) {
            HybridLogic.addBlood(sp, amount * 1.5f);
        }
    }

    /** The tongue stabs out and runs through the first thing in its way. */
    public static class Tongue extends DevilAbility {
        public Tongue() {
            super(HybridType.LEECH, "leech_tongue");
            timing(18, 60);
            cost(4);
            anim("", "tongue");
            fx("tongue");
            ai(3, 14, 12);
            reach(16);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 from = maw(user);
            LivingEntity t = target(run);
            Vec3 dir = t != null ? t.getBoundingBox().getCenter().subtract(from).normalize() : AbilityUtil.aim(user);
            Vec3 end = from.add(dir.scale(15));
            BlockHitResult block = level.clip(new ClipContext(from, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE,
                    user));
            Vec3 limit = block.getType() == HitResult.Type.MISS ? end : block.getLocation();
            AbilityUtil.sound(user, ModSounds.SPEAR_THROW.get(), 1.0f, 1.4f);
            List<LivingEntity> hits = AbilityUtil.alongLine(user, from, limit, 0.5);
            if (!hits.isEmpty()) {
                LivingEntity e = hits.get(0);
                limit = e.getBoundingBox().getCenter();
                AbilityUtil.hurtIgnoringIFrames(user, e, 12f);
                AbilityUtil.blood(level, limit, 30, 0.25);
                Fx.bloodSpray(level, limit, dir, 14, 0.4);
                AbilityUtil.push(e, e.position().add(dir), -0.4, 0.1);
                drink(user, 3f);
            }
            Fx.speedLine(level, from, limit);
            Fx.impact(level, limit, 0.9);
        }
    }

    /** Sucker-lined tentacles lash out and drag whatever they catch into reach of the mouth. */
    public static class Grab extends DevilAbility {
        public Grab() {
            super(HybridType.LEECH, "leech_grab");
            timing(24, 80);
            cost(6);
            anim("", "grab");
            ai(1, 8, 10);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 9) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.WHIP_LASH.get(), 1.0f, 0.7f);
            int n = 0;
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user), 9, 50)) {
                if (n++ >= 3) {
                    break;
                }
                AbilityUtil.hurt(user, e, 6f);
                AbilityUtil.push(e, user.position(), -1.1, 0.2);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 2)));
                Vec3 to = e.getBoundingBox().getCenter().subtract(maw(user));
                Fx.whipArc(level, maw(user), to.normalize(), new Vec3(0, 1, 0), to.length(), 0.3);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 8, 0.2);
            }
        }
    }

    /** The whole front of it is a mouth: it bites down on whatever is in front of it. */
    public static class Devour extends DevilAbility {
        public Devour() {
            super(HybridType.LEECH, "leech_devour");
            timing(16, 50);
            cost(4);
            anim("", "devour");
            ai(0, 3, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.4f, 0.6f);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    3.0 + user.getBbWidth() * 0.5, 60)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 18f);
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 45, 0.35);
                drink(user, 4f);
            }
            Fx.impact(level, maw(user), 1.4);
        }
    }

    /** It latches onto its prey and drinks it dry for two seconds. */
    public static class Drain extends DevilAbility {
        public Drain() {
            super(HybridType.LEECH, "leech_drain");
            timing(40, 120);
            cost(0);
            anim("", "drain");
            ai(0, 3, 6);
            reach(5);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            LivingEntity t = target(run);
            if (t == null || run.tick < 4 || run.tick % 6 != 0) {
                return;
            }
            if (t.distanceTo(user) > 3.5 + user.getBbWidth()) {
                return; // it tore free
            }
            ServerLevel level = level(user);
            AbilityUtil.hurtIgnoringIFrames(user, t, 3f);
            t.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 20, 4)));
            t.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 60, 1)));
            drink(user, 2f);
            AbilityUtil.blood(level, t.getBoundingBox().getCenter(), 10, 0.2);
            AbilityUtil.sound(user, ModSounds.BLOOD_DRINK.get(), 0.9f, 0.7f);
        }
    }

    private LeechMoves() {
    }
}
