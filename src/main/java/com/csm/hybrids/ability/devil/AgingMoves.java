package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.Tags;

import java.util.List;

/**
 * The Aging Devil, a Primal Devil (part 2): tall, thin and gaunt, a withered mass of flesh full of holes, its face
 * sliced in half, a second face that is only a mouth, feet like high heels. It ages what it touches - a bullet from
 * Yoru's strongest weapon crumbled to dust before it arrived - it put down the Chainsaw Devil with a single punch, and
 * it takes people away to a realm of its own, a forest by a lake.
 */
public final class AgingMoves {

    public static List<Ability> all() {
        return List.of(new Age(), new Punch(), new DustToDust(), new ForestByTheLake());
    }

    private static Vec3 flat(Vec3 v) {
        Vec3 f = new Vec3(v.x, 0, v.z);
        return f.lengthSqr() < 1e-4 ? new Vec3(0, 0, 1) : f.normalize();
    }

    /** It looks at its prey and the prey grows old: withering, slow, weak, grey. */
    public static class Age extends DevilAbility {
        public Age() {
            super(HybridType.AGING, "aging_wither");
            timing(20, 120);
            cost(6);
            anim("", "age");
            ai(2, 18, 12);
            reach(22);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 10) {
                return;
            }
            ServerLevel level = level(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user), 20, 10)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 8f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WITHER, 160, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 240, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 200, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DIG_SLOWDOWN, 240, 1)));
                Vec3 c = e.getBoundingBox().getCenter();
                Fx.smoke(level, c, 16, 0.4);
                Fx.stars(level, e.getEyePosition(), 4, 0.25);
                AbilityUtil.sound(user, ModSounds.COSMOS_VOID.get(), 1.2f, 0.4f);
                break;
            }
        }
    }

    /** One punch. It put the Chainsaw Devil down with a single one. */
    public static class Punch extends DevilAbility {
        public Punch() {
            super(HybridType.AGING, "aging_punch");
            timing(22, 100);
            cost(8);
            anim("", "punch");
            ai(0, 4, 10);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.DEVIL_GROWL.get(), 1.4f, 0.4f);
            }
            if (run.tick != 12) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 fist = user.position().add(0, user.getBbHeight() * 0.55, 0);
            AbilityUtil.sound(user, ModSounds.VIOLENCE_PUNCH.get(), 2.2f, 0.4f);
            Fx.impact(level, fist.add(flat(aim).scale(2.5 + user.getBbWidth() * 0.5)), 3.4);
            for (LivingEntity e : coneTargets(user, run, fist, aim, 4.0 + user.getBbWidth() * 0.5, 45)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 30f);
                Vec3 f = flat(e.position().subtract(user.position()));
                e.setDeltaMovement(f.x * 2.6, 0.7, f.z * 2.6);
                e.hurtMarked = true;
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 60, 0.5);
                Fx.shockwave(level, e.position(), 2.4, Fx.STEEL_RING);
            }
        }
    }

    /**
     * Everything around it ages all at once: arrows, bullets and whatever lies on the ground crumble to dust in the air,
     * and every living thing withers.
     */
    public static class DustToDust extends DevilAbility {
        public DustToDust() {
            super(HybridType.AGING, "aging_dust");
            timing(26, 300);
            cost(12);
            anim("", "dust");
            ai(0, 10, 6);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 c = user.position().add(0, user.getBbHeight() * 0.5, 0);
            double r = 10 + user.getBbWidth() * 0.5;
            if (run.tick == 6) {
                AbilityUtil.sound(user, ModSounds.COSMOS_VOID.get(), 2.0f, 0.3f);
            }
            if (run.tick >= 8 && run.tick <= 18 && run.tick % 3 == 2) {
                Fx.shockwave(level, user.position(), 3 + (run.tick - 8) * 0.8, Fx.STEEL_RING);
                // what flies at it or lies around it crumbles
                for (Entity e : level.getEntities(user, new AABB(c, c).inflate(r),
                        e -> (e instanceof Projectile p && p.getOwner() != user) || e instanceof ItemEntity)) {
                    Fx.smoke(level, e.position(), 4, 0.15);
                    e.discard();
                }
            }
            if (run.tick != 12) {
                return;
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, c, r)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 6f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WITHER, 120, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 120, 0)));
                Fx.smoke(level, e.getBoundingBox().getCenter(), 8, 0.3);
            }
        }
    }

    /**
     * It takes its prey away to its own realm - a lush forest by a lake - and lets it go somewhere else entirely:
     * far off, dazed, and older.
     */
    public static class ForestByTheLake extends DevilAbility {
        public ForestByTheLake() {
            super(HybridType.AGING, "aging_realm");
            timing(24, 600);
            cost(15);
            anim("", "realm");
            ai(2, 14, 3);
            reach(18);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 12) {
                return;
            }
            ServerLevel level = level(user);
            LivingEntity t = target(run);
            if (t == null || t.distanceTo(user) > reach + t.getBbWidth() || t.getType().is(Tags.EntityTypes.BOSSES)) {
                return;
            }
            Vec3 from = t.position();
            double a = level.random.nextDouble() * Math.PI * 2;
            double d = 40 + level.random.nextDouble() * 40;
            int x = (int) Math.floor(from.x + Math.cos(a) * d);
            int z = (int) Math.floor(from.z + Math.sin(a) * d);
            level.getChunk(x >> 4, z >> 4); // make sure there is ground to put it down on
            int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            if (y <= level.getMinBuildHeight()) {
                return;
            }
            Fx.smoke(level, t.getBoundingBox().getCenter(), 30, 0.6);
            Fx.stars(level, t.getEyePosition(), 12, 0.4);
            AbilityUtil.sound(user, ModSounds.COSMOS_HALLOWEEN.get(), 1.4f, 0.5f);
            if (t instanceof ServerPlayer sp) {
                sp.connection.teleport(x + 0.5, y, z + 0.5, sp.getYRot(), sp.getXRot());
                sp.displayClientMessage(Component.translatable("msg.csm.aging_realm").withStyle(ChatFormatting.GRAY), true);
            } else {
                t.teleportTo(x + 0.5, y, z + 0.5);
            }
            t.fallDistance = 0;
            t.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.CONFUSION, 160, 0)));
            t.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 400, 1)));
            t.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 200, 1)));
            Fx.smoke(level, t.getBoundingBox().getCenter(), 20, 0.6);
        }
    }

    private AgingMoves() {
    }
}
