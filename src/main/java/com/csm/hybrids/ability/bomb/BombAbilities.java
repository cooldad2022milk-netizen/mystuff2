package com.csm.hybrids.ability.bomb;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.HeadBombEntity;
import com.csm.hybrids.entity.SparkBombEntity;
import com.csm.hybrids.fx.Blast;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

/**
 * Reze's moves. Everything is an explosion: punches, kicks, flight, even her own head. Like in the manga the
 * Bomb Devil's power does not work while she is soaking wet.
 */
public final class BombAbilities {

    public static boolean tooWet(ServerPlayer player) {
        return player.isInWaterRainOrBubble();
    }

    /** Base for every bomb move: refuses to fire while wet. */
    public abstract static class BombAbility extends Ability {
        protected BombAbility(String id) {
            super(HybridType.BOMB, id);
        }

        @Override
        public String checkUse(ServerPlayer player, HybridData data) {
            String base = super.checkUse(player, data);
            if (base != null) {
                return base;
            }
            return tooWet(player) ? "msg.csm.too_wet" : null;
        }
    }

    /** Punch, punch, kick - each blow detonates on contact. */
    public static class ExplosiveCombo extends BombAbility {
        public ExplosiveCombo() {
            super("explosive_combo");
            timing(16, 20);
            anim("bomb_combo", "combo");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4 && run.tick != 9 && run.tick != 13) {
                return;
            }
            ServerLevel level = player.serverLevel();
            boolean kick = run.tick == 13;
            Vec3 look = player.getLookAngle();
            Vec3 at = kick ? player.position().add(look.x * 2.0, 0.7, look.z * 2.0)
                    : AbilityUtil.handPos(player, run.tick == 4, 2.0);
            player.setDeltaMovement(player.getDeltaMovement().add(look.x * 0.25, 0, look.z * 0.25));
            player.hurtMarked = true;
            Blast.detonate(level, player, null, at, kick ? 2.2f : 1.7f, kick ? 9f : 6.5f, false);
        }
    }

    /** A flick of the fingers sends out a spark that explodes on contact. */
    public static class SparkFlick extends BombAbility {
        public SparkFlick() {
            super("spark_flick");
            timing(10, 25);
            cost(2);
            anim("bomb_flick", "flick");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            Vec3 from = AbilityUtil.handPos(player, true, 0.8);
            SparkBombEntity spark = new SparkBombEntity(player.level(), player);
            spark.setPos(from.x, from.y, from.z);
            Vec3 look = player.getLookAngle();
            spark.shoot(look.x, look.y + 0.05, look.z, 1.6f, 0.2f);
            player.level().addFreshEntity(spark);
            Fx.fuseSparks(player.serverLevel(), from, 8);
            AbilityUtil.sound(player, ModSounds.BOMB_FUSE.get(), 1f, 1.8f);
        }
    }

    /** Explosions out of her feet and palms: rocket through the air. */
    public static class BlastPropulsion extends BombAbility {
        public BlastPropulsion() {
            super("blast_propulsion");
            timing(30, 70);
            cost(5);
            anim("bomb_propulsion", "propulsion");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            player.fallDistance = 0;
            if (run.tick < 3 || run.tick > 24 || run.tick % 4 != 3) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 behind = player.position().add(0, 0.3, 0).subtract(look.scale(0.9));
            Blast.detonate(level, player, null, behind, 1.8f, 5f, false);
            Vec3 v = player.getDeltaMovement().scale(0.3).add(look.scale(1.25)).add(0, 0.28, 0);
            player.setDeltaMovement(v);
            player.hurtMarked = true;
        }

        @Override
        public void end(ServerPlayer player, HybridData data, AbilityRun run) {
            player.fallDistance = 0;
        }
    }

    /** Her forearm becomes a torpedo: dash forward and detonate on whatever it hits. */
    public static class Torpedo extends BombAbility {
        public Torpedo() {
            super("torpedo");
            timing(20, 110);
            cost(8);
            anim("bomb_torpedo", "torpedo");
            fx("torpedo");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            if (run.tick == 5) {
                AbilityUtil.sound(player, ModSounds.BOMB_FUSE.get(), 1.2f, 0.7f);
            }
            if (run.tick >= 6 && run.tick <= 13 && run.counter == 0) {
                player.setDeltaMovement(look.scale(1.5));
                player.hurtMarked = true;
                player.fallDistance = 0;
                Vec3 nose = AbilityUtil.handPos(player, true, 1.3);
                Fx.fireJet(level, nose.subtract(look.scale(1.6)), look.scale(-1), 6, 0.25, 0.15);
                Fx.smoke(level, nose.subtract(look.scale(1.8)), 2, 0.15);
                // lifted a little so skimming the floor while looking slightly down doesn't set it off;
                // a wall, a mob or a real dive into the ground does
                if (!AbilityUtil.inRadius(player, nose, 1.6).isEmpty()
                        || !level.noCollision(player, player.getBoundingBox().move(look.scale(0.6)).move(0, 0.2, 0))) {
                    boom(player, level, nose, run);
                }
            }
            if (run.tick == 14 && run.counter == 0) {
                boom(player, level, AbilityUtil.handPos(player, true, 1.3), run);
            }
        }

        private static void boom(ServerPlayer player, ServerLevel level, Vec3 at, AbilityRun run) {
            run.counter = 1;
            player.setDeltaMovement(player.getLookAngle().scale(-0.6).add(0, 0.3, 0));
            player.hurtMarked = true;
            Blast.detonate(level, player, null, at, 3.6f, 16f, true);
        }
    }

    /** Pull the pin, tear off her own bomb head and throw it. A new one grows back. */
    public static class HeadBomb extends BombAbility {
        public HeadBomb() {
            super("head_bomb");
            timing(26, 240);
            cost(12);
            anim("bomb_head_throw", "headless");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 4) {
                AbilityUtil.sound(player, ModSounds.BOMB_PIN.get(), 1f, 0.8f);
            }
            if (run.tick == 9) {
                ServerLevel level = player.serverLevel();
                Vec3 from = player.getEyePosition().add(0, 0.2, 0).add(player.getLookAngle().scale(0.6));
                HeadBombEntity head = new HeadBombEntity(level, player);
                head.setPos(from.x, from.y, from.z);
                Vec3 look = player.getLookAngle();
                head.shoot(look.x, look.y + 0.25, look.z, 1.25f, 0.5f);
                level.addFreshEntity(head);
                AbilityUtil.blood(level, player.getEyePosition(), 26, 0.2);
                Fx.fuseSparks(level, player.getEyePosition(), 10);
                AbilityUtil.sound(player, ModSounds.SPEAR_THROW.get(), 1f, 0.7f);
            }
        }
    }

    private BombAbilities() {
    }
}
