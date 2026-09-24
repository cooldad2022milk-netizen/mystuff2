package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModEntities;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * Princi, the Spider Devil - one of Makima's. From the waist up a woman with long black hair and a zipper down the
 * middle of her face; below, a spider's body on eight legs sharp as knives. She walks on walls, sinks into the ground
 * and comes up under her prey, and she can unzip herself to let Makima step out, wherever she is.
 */
public final class SpiderMoves {
    /** Set on a devil called up by a move: it vanishes at this game time and leaves nothing behind. */
    public static final String SUMMONED_UNTIL = "csm_summoned_until";

    public static List<Ability> all() {
        return List.of(new Impale(), new ScytheLegs(), new Burrow(), new Unzip());
    }

    private static Vec3 flat(Vec3 v) {
        Vec3 f = new Vec3(v.x, 0, v.z);
        return f.lengthSqr() < 1e-4 ? new Vec3(0, 0, 1) : f.normalize();
    }

    /** She rears up and drives her two front legs down into her prey. */
    public static class Impale extends DevilAbility {
        public Impale() {
            super(HybridType.SPIDER, "spider_impale");
            timing(18, 40);
            anim("", "impale");
            ai(0, 3, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick == 3) {
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 0.8f, 1.6f);
            }
            if (run.tick != 7 && run.tick != 11) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            for (LivingEntity e : coneTargets(user, run, user.position().add(0, user.getBbHeight() * 0.5, 0), aim,
                    3.0 + user.getBbWidth() * 0.5, 45)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 12f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 2)));
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 30, 0.35);
                Fx.bloodSpray(level, c, aim, 12, 0.4);
            }
            AbilityUtil.sound(user, ModSounds.SPEAR_IMPACT.get(), 1.2f, run.tick == 7 ? 1.3f : 1.1f);
            Fx.slash(level, user.getEyePosition().add(aim.scale(1.5 + user.getBbWidth() * 0.4)), new Vec3(0, -1, 0), 1.8);
        }
    }

    /** All eight legs out: she spins and cuts everything around her. */
    public static class ScytheLegs extends DevilAbility {
        public ScytheLegs() {
            super(HybridType.SPIDER, "spider_scythe");
            timing(20, 120);
            cost(5);
            anim("", "scythe");
            ai(0, 4, 9);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.WHIP_LASH.get(), 1.4f, 1.4f);
            }
            if (run.tick < 6 || run.tick > 13) {
                return;
            }
            ServerLevel level = level(user);
            double r = 3.4 + user.getBbWidth() * 0.5;
            double a = (run.tick - 6) / 7.0 * Math.PI * 2;
            for (int k = 0; k < 2; k++) {
                double b = a + k * Math.PI;
                Fx.slash(level, user.position().add(Math.cos(b) * r * 0.7, 0.6, Math.sin(b) * r * 0.7),
                        new Vec3(-Math.sin(b), 0, Math.cos(b)), 2.0);
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position().add(0, 0.8, 0), r)) {
                if (run.hit.add(e.getId())) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 11f);
                    AbilityUtil.push(e, user.position(), 1.0, 0.3);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 24, 0.3);
                    AbilityUtil.sound(user, ModSounds.KATANA_SLASH.get(), 1.0f, 1.3f);
                }
            }
        }
    }

    /** She sinks into the ground, runs under it to her prey and bursts up beneath it, legs first. */
    public static class Burrow extends DevilAbility {
        public static final int BURST_TICK = 18;

        public Burrow() {
            super(HybridType.SPIDER, "spider_burrow");
            timing(26, 160);
            cost(6);
            anim("", "burrow");
            ai(4, 22, 8);
            mobile();
            blind();
            reach(26);
        }

        @Override
        public void begin(LivingEntity user, AbilityRun run) {
            super.begin(user, run);
            run.vec = user.position();
            LivingEntity t = target(run);
            if (t != null) {
                run.vec2 = t.position();
            } else {
                HitResult b = AbilityUtil.raycastBlock(user, reach);
                run.vec2 = b.getType() == HitResult.Type.MISS
                        ? user.position().add(flat(AbilityUtil.aim(user)).scale(14)) : b.getLocation();
            }
            AbilityUtil.sound(user, ModSounds.SHARK_DIVE.get(), 1.2f, 1.3f);
            Fx.clods(level(user), user.position(), 24, 0.4);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            user.fallDistance = 0;
            LivingEntity t = target(run);
            if (t != null) {
                run.vec2 = t.position();
            }
            if (run.vec == null || run.vec2 == null) {
                return;
            }
            if (run.tick >= 5 && run.tick < BURST_TICK) {
                // under the ground, towards the prey (the model has sunk out of sight)
                double f = Math.min(1, (run.tick - 4) / (double) (BURST_TICK - 6));
                Vec3 ground = AbilityUtil.groundBelow(level, run.vec.lerp(run.vec2, f), 6);
                if (ground != null) {
                    user.teleportTo(ground.x, ground.y, ground.z);
                    user.setDeltaMovement(Vec3.ZERO);
                }
                if (run.tick % 2 == 0) {
                    Fx.clods(level, user.position(), 3, 0.15);
                }
            }
            if (run.tick == BURST_TICK) {
                Vec3 at = user.position();
                AbilityUtil.sound(user, ModSounds.DEVIL_SCREECH.get(), 1.4f, 1.3f);
                AbilityUtil.sound(user, ModSounds.SPEAR_ERUPT.get(), 1.4f, 1.1f);
                Fx.clods(level, at, 40, 0.5);
                Fx.shockwave(level, at.add(0, 0.02, 0), 3.2, Fx.STEEL_RING);
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class,
                        new AABB(at, at).inflate(2.0 + user.getBbWidth() * 0.5, 2.5, 2.0 + user.getBbWidth() * 0.5),
                        e -> AbilityUtil.canHit(user, e))) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 16f);
                    e.setDeltaMovement(e.getDeltaMovement().add(0, 1.0, 0));
                    e.hurtMarked = true;
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 40, 0.35);
                }
                user.setDeltaMovement(0, 0.6, 0);
                user.hurtMarked = true;
            }
        }
    }

    /**
     * She pulls the zipper in her face down and Makima steps out of her - Princi can call her like that even into Hell.
     * Makima fights for you for 30 seconds, then is gone again (and leaves nothing behind).
     */
    public static class Unzip extends DevilAbility {
        public static final int SUMMON_TICKS = 600;

        public Unzip() {
            super(HybridType.SPIDER, "spider_unzip");
            timing(30, 6000);
            cost(40);
            anim("", "unzip");
            playerOnly();
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 front = user.position().add(flat(AbilityUtil.aim(user)).scale(user.getBbWidth() * 0.5 + 1.2));
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.CHAIN_THROW.get(), 1.0f, 1.8f); // the zipper
            }
            if (run.tick >= 6 && run.tick < 16 && run.tick % 2 == 0) {
                Fx.smoke(level, front.add(0, 1.0, 0), 4, 0.3);
                AbilityUtil.blood(level, user.getEyePosition(), 4, 0.1);
            }
            if (run.tick != 16) {
                return;
            }
            DevilEntity makima = ModEntities.devil(HybridType.CONTROL).create(level);
            if (makima == null) {
                return;
            }
            Vec3 ground = AbilityUtil.groundBelow(level, front, 4);
            Vec3 at = ground != null ? ground : front;
            makima.moveTo(at.x, at.y, at.z, user.getYRot(), 0f);
            makima.setYHeadRot(user.getYRot());
            makima.finalizeSpawn(level, level.getCurrentDifficultyAt(makima.blockPosition()), MobSpawnType.MOB_SUMMONED,
                    null, null);
            DevilEntity.enthrall(makima, user.getUUID());
            makima.getPersistentData().putLong(ControlMoves.THRALL_UNTIL, level.getGameTime() + SUMMON_TICKS);
            makima.getPersistentData().putLong(SUMMONED_UNTIL, level.getGameTime() + SUMMON_TICKS);
            level.addFreshEntity(makima);
            AbilityUtil.sound(user, ModSounds.CONTROL_DOMINATE.get(), 1.4f, 1.0f);
            Fx.shockwave(level, at.add(0, 0.05, 0), 3.0, Fx.BLOOD_RING);
            Fx.stars(level, at.add(0, 1.6, 0), 10, 0.3);
            if (user instanceof Player p) {
                p.displayClientMessage(Component.translatable("msg.csm.unzipped").withStyle(ChatFormatting.RED), true);
            }
        }
    }

    private SpiderMoves() {
    }
}
