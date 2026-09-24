package com.csm.hybrids.ability.shark;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Beam, the Shark Fiend. He swims through floors and walls like water, bites, can swell his head into a six-eyed
 * shark skull, or turn his whole body into a shark on long fin-legs (the one Denji rode). He can smell a hybrid.
 */
public final class SharkAbilities {

    static float power(HybridData data, float base) {
        return data.isTransformed() ? base * 1.5f : base;
    }

    /** True while the player is under the ground (can't be hit). */
    public static boolean submerged(Player player) {
        HybridData data = HybridCapability.get(player);
        return data != null && data.activeRun != null
                && (data.activeRun.ability instanceof GroundSwim
                || (data.activeRun.ability instanceof Ambush && data.activeRun.tick < Ambush.BURST_TICK));
    }

    /** Push through a wall in front: find the first free spot on the other side (up to 5 blocks). */
    static void phase(ServerPlayer player, Vec3 dir) {
        ServerLevel level = player.serverLevel();
        Vec3 flat = new Vec3(dir.x, 0, dir.z);
        if (flat.lengthSqr() < 1e-4) {
            return;
        }
        flat = flat.normalize();
        for (double d = 1.0; d <= 5.0; d += 0.5) {
            Vec3 off = flat.scale(d);
            if (level.noCollision(player, player.getBoundingBox().move(off))) {
                Vec3 p = player.position().add(off);
                Fx.clods(level, player.position(), 10, 0.2);
                player.connection.teleport(p.x, p.y, p.z, player.getYRot(), player.getXRot());
                Fx.clods(level, p, 10, 0.2);
                return;
            }
        }
    }

    /** Dive into the ground and swim through it - through walls too. Only the fin shows. */
    public static class GroundSwim extends Ability {
        public GroundSwim() {
            super(HybridType.SHARK, "ground_swim");
            anyForm();
            timing(100, 80);
            cost(3);
            anim("shark_swim", "swim");
            fx("swim");
        }

        @Override
        public void start(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 1.2f, 1f);
            Fx.clods(level, player.position(), 24, 0.35);
            Fx.shockwave(level, player.position().add(0, 0.02, 0), 1.8, Fx.STEEL_RING);
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 100, 2, false, false)));
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            player.fallDistance = 0;
            if (run.tick % 2 == 0) {
                Vec3 fin = player.position().add(0, 0.1, 0);
                Fx.clods(level, fin, 2, 0.12);
                level.sendParticles(com.csm.hybrids.registry.ModParticles.SMOKE.get(), fin.x, fin.y, fin.z, 1, 0.2, 0.02,
                        0.2, 0.01);
            }
            if (run.tick % 20 == 10) {
                AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 0.4f, 1.4f);
            }
            if (player.horizontalCollision && run.tick % 3 == 0) {
                phase(player, player.getLookAngle());
            }
        }

        @Override
        public void end(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 1.2f, 0.8f);
            Fx.clods(level, player.position(), 24, 0.4);
            player.removeEffect(MobEffects.MOVEMENT_SPEED);
            player.setDeltaMovement(player.getDeltaMovement().add(0, 0.5, 0));
            player.hurtMarked = true;
        }
    }

    /** Lunge and bite. */
    public static class Bite extends Ability {
        public Bite() {
            super(HybridType.SHARK, "shark_bite");
            anyForm();
            timing(12, 20);
            anim("shark_bite", "bite");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            if (run.tick == 3) {
                player.setDeltaMovement(look.x * 1.2, 0.15, look.z * 1.2);
                player.hurtMarked = true;
            }
            if (run.tick < 4 || run.tick > 8 || run.counter != 0) {
                return;
            }
            Vec3 jaws = player.getEyePosition().add(look.scale(1.2));
            for (LivingEntity e : AbilityUtil.inRadius(player, jaws, data.isTransformed() ? 2.4 : 1.8)) {
                run.counter = 1;
                AbilityUtil.hurtIgnoringIFrames(player, e, power(data, 12f));
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 40, 0.3);
                Fx.bloodSpray(level, c, look, 16, 0.4);
                Fx.impact(level, c, 1.2);
                AbilityUtil.sound(player, ModSounds.SHARK_BITE.get(), 1.3f, data.isTransformed() ? 0.7f : 1f);
                player.heal(2f);
                break;
            }
            if (run.tick == 8 && run.counter == 0) {
                AbilityUtil.sound(player, ModSounds.SHARK_BITE.get(), 0.7f, 1.3f);
            }
        }
    }

    /** Dive, swim under the target and burst out of the ground beneath it, jaws first. */
    public static class Ambush extends Ability {
        public static final int BURST_TICK = 20;

        public Ambush() {
            super(HybridType.SHARK, "shark_ambush");
            anyForm();
            timing(24, 100);
            cost(5);
            anim("shark_ambush", "ambush");
            fx("swim");
        }

        @Override
        public void start(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            EntityHitResult hit = AbilityUtil.raycastEntity(player, 28);
            if (hit != null && hit.getEntity() instanceof LivingEntity target) {
                run.target = target;
                run.vec2 = target.position();
            } else {
                HitResult b = AbilityUtil.raycastBlock(player, 28);
                run.vec2 = b.getType() == HitResult.Type.MISS
                        ? player.position().add(player.getLookAngle().multiply(1, 0, 1).normalize().scale(16)) : b.getLocation();
            }
            run.vec = player.position();
            AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 1.2f, 1f);
            Fx.clods(level, player.position(), 20, 0.35);
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            player.fallDistance = 0;
            if (run.target instanceof LivingEntity t && t.isAlive()) {
                run.vec2 = t.position();
            }
            if (run.tick < BURST_TICK && run.tick >= 2 && run.vec2 != null) {
                // swim towards the target under the ground
                double f = Math.min(1, (run.tick - 1) / (double) (BURST_TICK - 3));
                Vec3 p = run.vec.lerp(run.vec2, f);
                Vec3 ground = AbilityUtil.groundBelow(level, p, 6);
                if (ground != null) {
                    player.connection.teleport(ground.x, ground.y, ground.z, player.getYRot(), player.getXRot());
                }
                Fx.clods(level, player.position(), 2, 0.1);
            }
            if (run.tick == BURST_TICK) {
                Vec3 at = player.position();
                AbilityUtil.sound(player, ModSounds.SHARK_BITE.get(), 1.5f, 0.8f);
                AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 1.4f, 0.7f);
                Fx.clods(level, at, 40, 0.5);
                Fx.shockwave(level, at.add(0, 0.02, 0), 3.0, Fx.STEEL_RING);
                Fx.impact(level, at.add(0, 1, 0), 2.0);
                for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(2.2, 2.5, 2.2),
                        e -> AbilityUtil.canHit(player, e))) {
                    AbilityUtil.hurtIgnoringIFrames(player, e, power(data, 15f));
                    e.setDeltaMovement(e.getDeltaMovement().add(0, 1.0, 0));
                    e.hurtMarked = true;
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 40, 0.3);
                }
                player.setDeltaMovement(0, 0.8, 0);
                player.hurtMarked = true;
            }
        }
    }

    /**
     * Beam's whole body becomes a shark on long fin-legs: much faster, and everything he runs into gets rammed and
     * bitten.
     */
    public static class SharkForm extends Ability {
        public SharkForm() {
            super(HybridType.SHARK, "shark_form");
            anyForm();
            timing(200, 400);
            cost(12);
            anim("shark_form", "sharkform");
            fx("sharkform");
        }

        @Override
        public void start(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            AbilityUtil.sound(player, ModSounds.TRANSFORM.get(), 1.3f, 0.6f);
            AbilityUtil.blood(level, player.getEyePosition(), 40, 0.5);
            Fx.shockwave(level, player.position().add(0, 0.02, 0), 3.5, Fx.BLOOD_RING);
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 200, 3, false, false)));
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.JUMP, 200, 1, false, false)));
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            player.fallDistance = 0;
            if (run.tick % 10 == 0) {
                run.hit.clear();
            }
            Vec3 look = player.getLookAngle().multiply(1, 0, 1).normalize();
            Vec3 jaws = player.position().add(look.scale(1.8)).add(0, 0.7, 0);
            for (LivingEntity e : AbilityUtil.inRadius(player, jaws, 1.9)) {
                if (run.hit.add(e.getId()) && AbilityUtil.hurtIgnoringIFrames(player, e, 9f)) {
                    AbilityUtil.push(e, player.position(), 1.1, 0.35);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.3);
                    AbilityUtil.sound(player, ModSounds.SHARK_BITE.get(), 1.2f, 0.7f);
                }
            }
        }

        @Override
        public void end(ServerPlayer player, HybridData data, AbilityRun run) {
            player.removeEffect(MobEffects.MOVEMENT_SPEED);
            player.removeEffect(MobEffects.JUMP);
            AbilityUtil.sound(player, ModSounds.REVERT.get(), 1f, 0.8f);
            AbilityUtil.blood(player.serverLevel(), player.getEyePosition(), 20, 0.4);
        }
    }

    /** A shark smells blood: every wounded creature and every hybrid or fiend nearby lights up. */
    public static class BloodScent extends Ability {
        public BloodScent() {
            super(HybridType.SHARK, "blood_scent");
            anyForm();
            timing(20, 200);
            cost(2);
            anim("shark_scent", "scent");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = player.serverLevel();
            int found = 0;
            for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(48),
                    e -> e != player && e.isAlive())) {
                boolean devil = e instanceof Player p && HybridCapability.get(p) != null && HybridCapability.get(p).isHybrid();
                if (devil || e.getHealth() < e.getMaxHealth()) {
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.GLOWING, 240, 0, false, false)));
                    found++;
                }
            }
            AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 0.6f, 1.8f);
            Fx.shockwave(level, player.position().add(0, 0.02, 0), 6.0, Fx.BLOOD_RING);
            player.displayClientMessage(net.minecraft.network.chat.Component.translatable("msg.csm.scent", found)
                    .withStyle(net.minecraft.ChatFormatting.DARK_RED), true);
        }
    }

    private SharkAbilities() {
    }
}
