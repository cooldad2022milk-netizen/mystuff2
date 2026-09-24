package com.csm.hybrids.ability.violence;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Galgali, the Violence Fiend. Pure bare-handed violence: limbs swell with muscle for a blow. The plague-doctor mask
 * pumps poison into him to keep that in check; with it off he is huge and every hit is devastating (once both his arms
 * were cut off, he grew a new one out of his mouth).
 */
public final class ViolenceAbilities {

    /** Unmasked, Galgali hits several times harder. */
    static float power(HybridData data, float masked, float unmasked) {
        return data.isTransformed() ? unmasked : masked;
    }

    /** The arm swells with muscle for one haymaker. */
    public static class ViolentPunch extends Ability {
        public ViolentPunch() {
            super(HybridType.VIOLENCE, "violent_punch");
            anyForm();
            timing(16, 22);
            anim("violence_punch", "punch");
            fx("punch");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 7) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 fist = player.getEyePosition().add(look.scale(1.6)).add(0, -0.3, 0);
            boolean big = data.isTransformed();
            Fx.impact(level, fist, big ? 2.4 : 1.2);
            AbilityUtil.sound(player, ModSounds.VIOLENCE_PUNCH.get(), big ? 1.6f : 1.1f, big ? 0.7f : 1f);
            if (big) {
                Fx.shockwave(level, fist, 2.2, Fx.STEEL_RING);
            }
            for (LivingEntity e : AbilityUtil.inCone(player, big ? 4.5 : 3.6, 35)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, power(data, 9f, 22f))) {
                    AbilityUtil.push(e, player.position(), big ? 2.6 : 1.3, big ? 0.6 : 0.3);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), big ? 40 : 18, 0.3);
                }
            }
        }
    }

    /** The leg swells and stamps: the ground fractures. */
    public static class CrushingKick extends Ability {
        public CrushingKick() {
            super(HybridType.VIOLENCE, "crushing_kick");
            anyForm();
            timing(18, 40);
            cost(2);
            anim("violence_kick", "kick");
            fx("kick");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 9) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 at = player.position().add(look.x * 1.6, 0, look.z * 1.6);
            boolean big = data.isTransformed();
            double r = big ? 4.0 : 2.8;
            AbilityUtil.sound(player, ModSounds.VIOLENCE_PUNCH.get(), 1.4f, 0.6f);
            AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 1.0f, 0.6f);
            Fx.clods(level, at, big ? 40 : 20, 0.4);
            Fx.shockwave(level, at.add(0, 0.02, 0), r * 1.3, Fx.STEEL_RING);
            Fx.impact(level, at.add(0, 0.4, 0), big ? 2.4 : 1.4);
            for (LivingEntity e : AbilityUtil.inRadius(player, at.add(0, 0.8, 0), r)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, power(data, 11f, 20f))) {
                    AbilityUtil.push(e, at, big ? 1.4 : 0.8, big ? 0.9 : 0.5);
                }
            }
        }
    }

    /** A third arm bursts out of his mouth, grabs whatever is in front and punches it. Mask off only. */
    public static class MouthArm extends Ability {
        public MouthArm() {
            super(HybridType.VIOLENCE, "mouth_arm");
            timing(22, 80);
            cost(5);
            anim("violence_mouth_arm", "mouth_arm");
            fx("moutharm");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 4) {
                AbilityUtil.blood(level, player.getEyePosition().add(player.getLookAngle().scale(0.4)), 24, 0.15);
                AbilityUtil.sound(player, ModSounds.BLOOD_FORM.get(), 1.2f, 0.6f);
            }
            if (run.tick == 8) {
                EntityHitResult hit = AbilityUtil.raycastEntity(player, 6.5);
                if (hit != null && hit.getEntity() instanceof LivingEntity target) {
                    run.target = target;
                    Vec3 to = player.getEyePosition().add(player.getLookAngle().scale(1.6)).subtract(0, target.getBbHeight() * 0.5, 0);
                    target.teleportTo(to.x, Math.max(to.y, player.getY()), to.z);
                    Fx.impact(level, target.getBoundingBox().getCenter(), 1.2);
                }
            }
            if (run.tick == 13 && run.target instanceof LivingEntity target && target.isAlive()) {
                Vec3 c = target.getBoundingBox().getCenter();
                AbilityUtil.hurtIgnoringIFrames(player, target, 18f);
                AbilityUtil.push(target, player.position(), 2.2, 0.5);
                AbilityUtil.blood(level, c, 50, 0.35);
                Fx.impact(level, c, 2.4);
                Fx.shockwave(level, c, 2.0, Fx.BLOOD_RING);
                AbilityUtil.sound(player, ModSounds.VIOLENCE_PUNCH.get(), 1.6f, 0.6f);
            }
        }
    }

    /** Unrestrained: a rampage of punches while pushing forward. Mask off only. */
    public static class Rampage extends Ability {
        public Rampage() {
            super(HybridType.VIOLENCE, "rampage");
            timing(32, 140);
            cost(8);
            anim("violence_rampage", "rampage");
            fx("punch");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick < 3 || run.tick > 28 || run.tick % 3 != 0) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            boolean right = (run.tick / 3) % 2 == 0;
            Vec3 fist = AbilityUtil.handPos(player, right, 1.6);
            Fx.impact(level, fist, 1.3);
            player.setDeltaMovement(player.getDeltaMovement().add(look.x * 0.1, 0, look.z * 0.1));
            player.hurtMarked = true;
            AbilityUtil.sound(player, ModSounds.VIOLENCE_PUNCH.get(), 1f, 0.8f + level.random.nextFloat() * 0.4f);
            for (LivingEntity e : AbilityUtil.inCone(player, 4.0, 60)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, 7f)) {
                    AbilityUtil.push(e, player.position(), 0.5, 0.15);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 14, 0.3);
                }
            }
        }
    }

    private ViolenceAbilities() {
    }
}
