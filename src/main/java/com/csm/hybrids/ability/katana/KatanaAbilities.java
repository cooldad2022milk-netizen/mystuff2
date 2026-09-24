package com.csm.hybrids.ability.katana;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * Katana Man. Katana blades push out of both forearms; his signature is the Sword-Draw Dash - an iaijutsu quick-draw
 * so fast it looks like teleportation, the cut only opening once he is already past.
 */
public final class KatanaAbilities {

    /** Crouch as if drawing, vanish past everything in front, and a beat later they all split open. */
    public static class SwordDrawDash extends Ability {
        public static final int DASH_TICK = 9;
        public static final int CUT_TICK = 19;

        public SwordDrawDash() {
            super(HybridType.KATANA, "sword_draw_dash");
            timing(28, 120);
            cost(8);
            anim("katana_iai", "iai");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick < DASH_TICK) {
                // coiled, perfectly still
                player.setDeltaMovement(0, Math.min(player.getDeltaMovement().y, 0), 0);
                player.hurtMarked = true;
                if (run.tick == 2) {
                    AbilityUtil.sound(player, ModSounds.KATANA_DRAW.get(), 0.6f, 1.6f);
                }
                return;
            }
            if (run.tick == DASH_TICK) {
                Vec3 look = player.getLookAngle();
                Vec3 flat = new Vec3(look.x, 0, look.z).normalize();
                Vec3 from = player.position();
                // furthest free spot along the dash, up to 12 blocks
                Vec3 to = from;
                for (double d = 0.5; d <= 12.0; d += 0.5) {
                    Vec3 p = from.add(flat.scale(d));
                    if (!level.noCollision(player, player.getBoundingBox().move(p.subtract(from)))) {
                        break;
                    }
                    to = p;
                }
                for (LivingEntity e : AbilityUtil.alongLine(player, from.add(0, 0.9, 0), to.add(0, 0.9, 0), 0.9)) {
                    run.hit.add(e.getId());
                }
                for (int i = 0; i < 5; i++) {
                    double y = 0.3 + i * 0.35;
                    Fx.speedLine(level, from.add(0, y, 0), to.add(0, y, 0));
                }
                player.connection.teleport(to.x, to.y, to.z, player.getYRot(), player.getXRot());
                player.fallDistance = 0;
                AbilityUtil.sound(player, ModSounds.KATANA_IAI.get(), 1.4f, 1.0f);
                Fx.impact(level, to.add(0, 1.0, 0), 1.2);
                run.vec = flat;
                return;
            }
            if (run.tick == CUT_TICK) {
                boolean any = false;
                for (int id : run.hit) {
                    Entity e = level.getEntity(id);
                    if (e instanceof LivingEntity target && target.isAlive()) {
                        any = true;
                        Vec3 c = target.getBoundingBox().getCenter();
                        AbilityUtil.hurtIgnoringIFrames(player, target, 20f);
                        AbilityUtil.blood(level, c, 45, 0.35);
                        Fx.bloodSpray(level, c, run.vec == null ? Vec3.ZERO : run.vec, 26, 0.55);
                        Fx.slash(level, c, run.vec == null ? player.getLookAngle() : run.vec, 1.8);
                    }
                }
                if (any) {
                    AbilityUtil.sound(player, ModSounds.KATANA_SLASH.get(), 1.4f, 0.8f);
                }
            }
        }
    }

    /** Both forearm katanas cross in an X. */
    public static class TwinSlash extends Ability {
        public TwinSlash() {
            super(HybridType.KATANA, "twin_slash");
            timing(14, 18);
            anim("katana_twin", "twin");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 5) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 c = player.getEyePosition().add(look.scale(1.8)).add(0, -0.3, 0);
            Vec3 right = AbilityUtil.right(player);
            Fx.slash(level, c, look.add(right.scale(0.6)).add(0, 0.6, 0), 2.2);
            Fx.slash(level, c, look.subtract(right.scale(0.6)).add(0, 0.6, 0), 2.2);
            Fx.sparks(level, c, look, 10, 0.4);
            AbilityUtil.sound(player, ModSounds.KATANA_SLASH.get(), 1.1f, 1.1f);
            for (LivingEntity e : AbilityUtil.inCone(player, 4.8, 55)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, 11f)) {
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.3);
                    AbilityUtil.push(e, player.position(), 0.5, 0.15);
                }
            }
        }
    }

    /** A storm of quick cuts and thrusts. */
    public static class BladeFlurry extends Ability {
        public BladeFlurry() {
            super(HybridType.KATANA, "blade_flurry");
            timing(22, 60);
            cost(3);
            anim("katana_flurry", "flurry");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick < 3 || run.tick > 18 || run.tick % 3 != 0) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            boolean right = (run.tick / 3) % 2 == 0;
            Vec3 side = AbilityUtil.right(player).scale(right ? 0.9 : -0.9);
            Vec3 c = player.getEyePosition().add(look.scale(1.6)).add(0, -0.25, 0);
            Fx.slash(level, c, look.add(side).add(0, (run.tick % 2) * 0.8 - 0.4, 0), 1.5);
            AbilityUtil.sound(player, ModSounds.KATANA_SLASH.get(), 0.8f, 1.2f + level.random.nextFloat() * 0.3f);
            player.setDeltaMovement(player.getDeltaMovement().add(look.x * 0.12, 0, look.z * 0.12));
            player.hurtMarked = true;
            for (LivingEntity e : AbilityUtil.inCone(player, 4.2, 40)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, 4.5f)) {
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 12, 0.25);
                }
            }
        }
    }

    /**
     * Iai stance: hand on the hilt, waiting. The first blow that comes in is cut down before it lands
     * (see HybridEvents).
     */
    public static class IaiCounter extends Ability {
        public IaiCounter() {
            super(HybridType.KATANA, "iai_counter");
            timing(30, 80);
            cost(2);
            anim("katana_counter", "stance");
        }

        @Override
        public void start(ServerPlayer player, HybridData data, AbilityRun run) {
            AbilityUtil.sound(player, ModSounds.KATANA_DRAW.get(), 0.5f, 1.8f);
        }

        /** Called from HybridEvents when something attacks the player during the stance. */
        public static void counter(ServerPlayer player, AbilityRun run, Entity attacker) {
            if (run.counter != 0) {
                return;
            }
            run.counter = 1;
            ServerLevel level = player.serverLevel();
            AbilityUtil.sound(player, ModSounds.KATANA_IAI.get(), 1.3f, 1.2f);
            Fx.sparks(level, player.getEyePosition().add(player.getLookAngle().scale(0.8)), player.getLookAngle(), 16, 0.5);
            if (attacker instanceof LivingEntity target && AbilityUtil.canHit(player, target)) {
                Vec3 c = target.getBoundingBox().getCenter();
                if (target.distanceTo(player) < 6) {
                    AbilityUtil.hurtIgnoringIFrames(player, target, 16f);
                    AbilityUtil.blood(level, c, 40, 0.3);
                    Fx.slash(level, c, c.subtract(player.getEyePosition()), 2.0);
                    AbilityUtil.push(target, player.position(), 0.8, 0.2);
                }
            }
            run.duration = Math.min(run.duration, run.tick + 8);
        }
    }

    private KatanaAbilities() {
    }
}
