package com.csm.hybrids.ability.cosmos;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModEffects;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Cosmo, the Cosmos Fiend. She only ever says "Halloween". Her power, Total Understanding, forces a mind to grasp the
 * entire universe at once; the victim is left catatonic, thinking nothing but "Halloween". A full Halloween drags minds
 * into the library-like dimension inside her head.
 */
public final class CosmosAbilities {

    static void bolt(ServerLevel level, Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        int n = (int) Math.max(4, d.length() * 3);
        for (int i = 0; i <= n; i++) {
            Vec3 p = from.add(d.scale(i / (double) n));
            level.sendParticles(com.csm.hybrids.registry.ModParticles.STAR.get(), p.x, p.y, p.z, 1, 0.05, 0.05, 0.05, 0.0);
        }
    }

    static void mindBlown(ServerLevel level, LivingEntity e, int ticks, int amp) {
        e.addEffect(AbilityUtil.quiet(new MobEffectInstance(ModEffects.HALLOWEEN.get(), ticks, amp)));
        Fx.halloween(level, e.getEyePosition().add(0, 0.5, 0));
        Fx.stars(level, e.getEyePosition(), 12, 0.4);
    }

    /** "Halloween." One mind is shown the whole universe. */
    public static class Halloween extends Ability {
        public Halloween() {
            super(HybridType.COSMOS, "halloween");
            anyForm();
            timing(14, 60);
            cost(4);
            anim("cosmos_halloween", "halloween");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 2) {
                AbilityUtil.sound(player, ModSounds.COSMOS_HALLOWEEN.get(), 1f, 1f);
                Fx.stars(level, player.getEyePosition().add(0, 0.3, 0), 10, 0.3);
            }
            if (run.tick != 6) {
                return;
            }
            EntityHitResult hit = AbilityUtil.raycastEntity(player, 22);
            if (hit != null && hit.getEntity() instanceof LivingEntity target) {
                bolt(level, player.getEyePosition(), target.getEyePosition());
                mindBlown(level, target, data.isTransformed() ? 160 : 110, data.isTransformed() ? 1 : 0);
                AbilityUtil.soundAt(level, target.getEyePosition(), ModSounds.COSMOS_HALLOWEEN.get(), 1f, 0.9f);
            } else {
                bolt(level, player.getEyePosition(), player.getEyePosition().add(player.getLookAngle().scale(10)));
            }
        }
    }

    /**
     * All-Out Halloween: every mind around her is dragged into the endless library in her head. Needs her cosmos
     * opened.
     */
    public static class AllOutHalloween extends Ability {
        public AllOutHalloween() {
            super(HybridType.COSMOS, "all_out_halloween");
            timing(32, 300);
            cost(16);
            anim("cosmos_all_out", "all_out");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            Vec3 head = player.getEyePosition().add(0, 0.2, 0);
            if (run.tick < 14 && run.tick % 2 == 0) {
                // the universe gathering in her open skull
                Fx.stars(level, head, 6, 1.2 - run.tick * 0.07);
            }
            if (run.tick == 2) {
                AbilityUtil.sound(player, ModSounds.COSMOS_VOID.get(), 1.6f, 1f);
            }
            if (run.tick != 14) {
                return;
            }
            AbilityUtil.sound(player, ModSounds.COSMOS_HALLOWEEN.get(), 2f, 0.7f);
            for (int i = 0; i < 60; i++) {
                double a = i / 60.0 * Math.PI * 2;
                Vec3 p = head.add(Math.cos(a) * 3, level.random.nextGaussian() * 0.8, Math.sin(a) * 3);
                level.sendParticles(com.csm.hybrids.registry.ModParticles.STAR.get(), p.x, p.y, p.z, 0,
                        Math.cos(a) * 0.6, 0.02, Math.sin(a) * 0.6, 1.0);
            }
            for (LivingEntity e : AbilityUtil.inRadius(player, head, 12)) {
                bolt(level, head, e.getEyePosition());
                mindBlown(level, e, 220, 1);
            }
        }
    }

    /** Knowing everything: every living thing within 48 blocks is revealed, even through walls. */
    public static class InfiniteKnowledge extends Ability {
        public InfiniteKnowledge() {
            super(HybridType.COSMOS, "infinite_knowledge");
            anyForm();
            timing(20, 240);
            cost(4);
            anim("cosmos_knowledge", "knowledge");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = player.serverLevel();
            for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(48),
                    e -> e != player && e.isAlive())) {
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.GLOWING, 300, 0, false, false)));
            }
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.NIGHT_VISION, 300, 0, false, false)));
            Fx.stars(level, player.getEyePosition().add(0, 0.3, 0), 30, 0.8);
            AbilityUtil.sound(player, ModSounds.COSMOS_VOID.get(), 0.8f, 1.5f);
        }
    }

    /**
     * Minds already drowning in the universe give way completely: every Halloween-struck target she looks at takes
     * damage for the time it had left.
     */
    public static class MindCollapse extends Ability {
        public MindCollapse() {
            super(HybridType.COSMOS, "mind_collapse");
            anyForm();
            timing(16, 100);
            cost(6);
            anim("cosmos_collapse", "collapse");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = player.serverLevel();
            int n = 0;
            for (LivingEntity e : AbilityUtil.inCone(player, 18, 40)) {
                MobEffectInstance fx = e.getEffect(ModEffects.HALLOWEEN.get());
                if (fx == null) {
                    continue;
                }
                n++;
                float dmg = Math.min(30f, 6f + fx.getDuration() / 20f * 2.5f);
                e.removeEffect(ModEffects.HALLOWEEN.get());
                AbilityUtil.hurtIgnoringIFrames(player, e, dmg);
                AbilityUtil.blood(level, e.getEyePosition(), 30, 0.2);
                Fx.stars(level, e.getEyePosition(), 30, 0.6);
                Fx.impact(level, e.getEyePosition(), 1.6);
            }
            AbilityUtil.sound(player, ModSounds.COSMOS_VOID.get(), 1.2f, n > 0 ? 0.6f : 1.4f);
        }
    }

    private CosmosAbilities() {
    }
}
