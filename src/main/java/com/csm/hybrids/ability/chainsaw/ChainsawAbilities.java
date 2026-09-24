package com.csm.hybrids.ability.chainsaw;

import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.ChainHookEntity;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.Tags;

/** Denji's moves. */
public final class ChainsawAbilities {

    /** Two brutal horizontal cuts with the forearm chainsaws. */
    public static class Slash extends Ability {
        public Slash() {
            super(HybridType.CHAINSAW, "chainsaw_slash");
            timing(14, 14);
            anim("chainsaw_slash", "slash");
            revs();
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 0) {
                AbilityUtil.sound(player, ModSounds.CHAINSAW_REV.get(), 1f, 1.1f);
            }
            if (run.tick == 4 || run.tick == 9) {
                ServerLevel level = player.serverLevel();
                boolean any = false;
                for (LivingEntity e : AbilityUtil.inCone(player, 3.9, 62)) {
                    if (AbilityUtil.hurtIgnoringIFrames(player, e, 9f)) {
                        any = true;
                        AbilityUtil.push(e, player.position(), 0.35, 0.12);
                        AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 26, 0.3);
                        Fx.bloodSpray(level, e.getBoundingBox().getCenter(), player.getLookAngle(), 14, 0.45);
                        Fx.sparks(level, e.getBoundingBox().getCenter(), player.getLookAngle().scale(-1), 8, 0.4);
                    }
                }
                Vec3 sweep = player.getEyePosition().add(player.getLookAngle().scale(1.6)).add(0, -0.3, 0);
                Fx.slash(level, sweep, player.getLookAngle(), 2.2);
                AbilityUtil.sound(player, any ? ModSounds.CHAINSAW_CUT.get() : ModSounds.CHAINSAW_REV.get(), 1f,
                        run.tick == 4 ? 1f : 1.15f);
            }
        }
    }

    /** Charge headfirst, the forehead saw screaming through everything in the way. */
    public static class HeadsawCharge extends Ability {
        public HeadsawCharge() {
            super(HybridType.CHAINSAW, "headsaw_charge");
            timing(18, 90);
            cost(5);
            anim("chainsaw_headsaw", "headbutt");
            revs();
        }

        @Override
        public void start(ServerPlayer player, HybridData data, AbilityRun run) {
            Vec3 look = player.getLookAngle();
            Vec3 flat = new Vec3(look.x, 0, look.z);
            run.vec = (flat.lengthSqr() < 1e-4 ? new Vec3(0, 0, 1) : flat.normalize());
            AbilityUtil.sound(player, ModSounds.CHAINSAW_REV.get(), 1.2f, 0.9f);
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick < 3 || run.tick > 14) {
                return;
            }
            Vec3 v = run.vec.scale(1.25);
            player.setDeltaMovement(v.x, Math.min(player.getDeltaMovement().y, 0.05), v.z);
            player.hurtMarked = true;
            player.fallDistance = 0;
            ServerLevel level = player.serverLevel();
            Vec3 tip = player.getEyePosition().add(run.vec.scale(1.7));
            Fx.sparks(level, tip, run.vec, 5, 0.35);
            if (run.tick % 2 == 0) {
                Vec3 mid = player.position().add(0, 1.0, 0);
                Fx.speedLine(level, mid.add(run.vec.scale(0.5)), mid.subtract(run.vec.scale(2.5)));
            }
            for (LivingEntity e : AbilityUtil.inRadius(player, tip.add(0, -0.4, 0), 1.7)) {
                if (run.hit.add(e.getId())) {
                    AbilityUtil.hurtIgnoringIFrames(player, e, 14f);
                    AbilityUtil.push(e, player.position(), 1.3, 0.45);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 40, 0.35);
                    Fx.impact(level, e.getBoundingBox().getCenter(), 1.6);
                    AbilityUtil.sound(player, ModSounds.CHAINSAW_CUT.get(), 1.2f, 0.9f);
                }
            }
        }
    }

    /** Fires a chain from the wrist: hooks a block to pull yourself in, or binds a target and drags it over. */
    public static class ChainGrapple extends Ability {
        public ChainGrapple() {
            super(HybridType.CHAINSAW, "chain_grapple");
            timing(9, 60);
            cost(3);
            anim("chainsaw_chain_throw", "throw");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 3) {
                ChainHookEntity hook = new ChainHookEntity(player.level(), player);
                Vec3 from = AbilityUtil.handPos(player, true, 0.6);
                hook.setPos(from.x, from.y, from.z);
                hook.shoot(player.getLookAngle().x, player.getLookAngle().y, player.getLookAngle().z, 2.6f, 0f);
                player.level().addFreshEntity(hook);
                AbilityUtil.sound(player, ModSounds.CHAIN_THROW.get(), 1f, 1f);
            }
        }
    }

    /** Grab the thing in front of you and saw straight through it (the classic Chainsaw Man finisher). */
    public static class RipAndTear extends Ability {
        public RipAndTear() {
            super(HybridType.CHAINSAW, "rip_and_tear");
            timing(32, 200);
            cost(8);
            anim("chainsaw_rip", "rip");
            revs();
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 2) {
                EntityHitResult hit = AbilityUtil.raycastEntity(player, 4.2);
                if (hit != null && hit.getEntity() instanceof LivingEntity target) {
                    run.target = target;
                    AbilityUtil.sound(player, ModSounds.CHAINSAW_REV.get(), 1.3f, 0.8f);
                } else {
                    run.failed = true;
                    run.duration = Math.min(run.duration, 10);
                    AbilityUtil.sound(player, ModSounds.CHAINSAW_REV.get(), 1f, 1.2f);
                }
                return;
            }
            if (run.failed || !(run.target instanceof LivingEntity target) || !target.isAlive()) {
                return;
            }
            if (run.tick >= 3 && run.tick <= 28) {
                boolean movable = !target.getType().is(Tags.EntityTypes.BOSSES) && target.getBbWidth() < 3f;
                if (movable) {
                    Vec3 look = player.getLookAngle();
                    Vec3 flat = new Vec3(look.x, 0, look.z).normalize();
                    Vec3 hold = player.position().add(flat.scale(1.1 + target.getBbWidth() * 0.5));
                    if (target instanceof ServerPlayer sp) {
                        sp.connection.teleport(hold.x, player.getY(), hold.z, sp.getYRot(), sp.getXRot());
                    } else {
                        target.teleportTo(hold.x, player.getY(), hold.z);
                    }
                    target.setDeltaMovement(Vec3.ZERO);
                    target.hurtMarked = true;
                }
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 3, 3, false, false, false)));
                if (run.tick % 3 == 0) {
                    AbilityUtil.hurtIgnoringIFrames(player, target, 3.5f);
                    AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 30, 0.3);
                    Fx.bloodSpray(level, target.getBoundingBox().getCenter(), player.getLookAngle().scale(-1).add(0, 0.6, 0), 16, 0.5);
                    Fx.sparks(level, target.getBoundingBox().getCenter(), player.getLookAngle().scale(-1), 6, 0.45);
                    if (run.tick % 6 == 0) {
                        AbilityUtil.sound(player, ModSounds.CHAINSAW_CUT.get(), 1.1f, 0.9f + level.random.nextFloat() * 0.2f);
                    }
                }
            }
            if (run.tick == 29) {
                AbilityUtil.hurtIgnoringIFrames(player, target, 10f);
                AbilityUtil.push(target, player.position(), 1.6, 0.5);
                AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 90, 0.5);
                Fx.impact(level, target.getBoundingBox().getCenter(), 2.4);
                Fx.shockwave(level, target.position(), 3.0, Fx.BLOOD_RING);
                AbilityUtil.sound(player, ModSounds.CHAINSAW_CUT.get(), 1.4f, 0.7f);
            }
        }
    }

    /** Chainsaws erupt from the shins for a full spinning kick. */
    public static class LegSawSpin extends Ability {
        public LegSawSpin() {
            super(HybridType.CHAINSAW, "leg_saw_spin");
            timing(17, 110);
            cost(6);
            anim("chainsaw_leg_spin", "leg_spin");
            fx("legsaw");
            revs();
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 2) {
                AbilityUtil.sound(player, ModSounds.CHAINSAW_REV.get(), 1.2f, 1.2f);
                AbilityUtil.blood(level, player.position().add(0, 0.4, 0), 20, 0.25);
                Fx.shockwave(level, player.position(), 3.6, Fx.BLOOD_RING);
            }
            if (run.tick >= 5 && run.tick <= 11) {
                double a = (run.tick - 5) / 6.0 * Math.PI * 2;
                for (int i = 0; i < 3; i++) {
                    double b = a + i * 0.35;
                    Fx.slash(level, new Vec3(player.getX() + Math.cos(b) * 1.3, player.getY() + 0.45,
                            player.getZ() + Math.sin(b) * 1.3), new Vec3(-Math.sin(b), 0, Math.cos(b)), 1.8);
                }
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 0.6, 0), 3.7)) {
                    if (run.hit.add(e.getId())) {
                        AbilityUtil.hurtIgnoringIFrames(player, e, 10f);
                        AbilityUtil.push(e, player.position(), 1.0, 0.3);
                        AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.3);
                        AbilityUtil.sound(player, ModSounds.CHAINSAW_CUT.get(), 1f, 1.1f);
                    }
                }
            }
        }
    }

    private ChainsawAbilities() {
    }
}
