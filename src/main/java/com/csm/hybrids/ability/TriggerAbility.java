package com.csm.hybrids.ability;

import com.csm.hybrids.ability.bomb.BombAbilities;
import com.csm.hybrids.fx.Blast;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.network.AnimSpec;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * Slot 0 of every wheel: the manga trigger.
 * <ul>
 *   <li>Chainsaw: grab the starter cord hanging out of the chest and yank it - the engine catches and
 *       chainsaws burst out of the forehead and forearms. With no blood in the tank the engine only sputters.</li>
 *   <li>Crossbow: reach up to the right eye socket and slowly draw out the arrow buried there.</li>
 *   <li>Flamethrower: bite down on the trigger molar. The click also restores the body to peak condition.</li>
 *   <li>Whip: snap the fingers like the crack of a whip - whips tear out of both hands.</li>
 *   <li>Bomb: hook a finger through the grenade pin under the choker and pull. She goes off on the spot.
 *       Soaked, the fuse will not light.</li>
 *   <li>Spear: reach behind the neck and draw a spear out of the nape.</li>
 *   <li>Katana / Longsword: pull off the left / right hand - the blade inside rises out of the stump. Putting the
 *       sword away leaves them spent for a while (they can't transform again straight away).</li>
 *   <li>Fiends: unleash the devil side - Power's horns grow, Beam's head becomes a six-eyed shark skull, Galgali
 *       takes his mask off, Cosmo opens the cosmos, the Gun Devil sprouts barrels.</li>
 * </ul>
 * Using it again while transformed puts the devil back away.
 */
public class TriggerAbility extends Ability {
    public static final float TRANSFORM_COST = 10f;

    public TriggerAbility(HybridType type, String id) {
        super(type, id);
        anyForm();
        timing(type.triggerTicks, 20);
        cost(TRANSFORM_COST);
    }

    @Override
    public boolean isTrigger() {
        return true;
    }

    @Override
    public boolean consumesBloodOnStart() {
        return false;
    }

    @Override
    public String checkUse(ServerPlayer player, HybridData data) {
        if (type.monster() && !data.isTransformed() && !roomToManifest(player)) {
            return "msg.csm.no_room";
        }
        return null; // a failed start is part of the fantasy (the engine sputters)
    }

    /** A monster devil's true form is bigger than a person: it needs the space to stand up in. */
    private boolean roomToManifest(ServerPlayer player) {
        com.csm.hybrids.devil.DevilSpec spec = com.csm.hybrids.devil.DevilSpecs.of(type);
        double hw = spec.playerWidth / 2.0;
        net.minecraft.world.phys.AABB box = new net.minecraft.world.phys.AABB(player.getX() - hw, player.getY() + 0.01,
                player.getZ() - hw, player.getX() + hw, player.getY() + spec.playerHeight, player.getZ() + hw);
        return player.level().noCollision(player, box);
    }

    @Override
    public void prepare(ServerPlayer player, HybridData data, AbilityRun run) {
        run.reverting = data.isTransformed();
        String p = type.animPrefix;
        if (type.devil) {
            // monster devils share one body animation (the human shell convulses and the devil tears out of it);
            // humanoid devils each have their own
            String body = type.monster() ? "devil" : p;
            if (run.reverting) {
                run.duration = type.revertTicks;
                run.anim = new AnimSpec(body + "_revert", "form", "", "", false, AnimSpec.REVERT, run.duration);
            } else {
                run.duration = type.triggerTicks;
                run.failed = data.blood() < TRANSFORM_COST;
                run.anim = new AnimSpec(body + "_" + (type.monster() ? "manifest" : "trigger"), "trigger",
                        type.humanoid ? "unleash" : "", "", false, AnimSpec.TRANSFORM, run.duration);
            }
            return;
        }
        if (run.reverting) {
            run.duration = type.revertTicks;
            run.anim = new AnimSpec(p + "_revert", "form", "", "", false, AnimSpec.REVERT, run.duration);
        } else {
            run.duration = type.triggerTicks;
            run.failed = data.blood() < TRANSFORM_COST || (type == HybridType.BOMB && BombAbilities.tooWet(player));
            String geo = switch (type) {
                case CHAINSAW -> "cord_snap";
                case CROSSBOW -> "pull_arrow";
                case BOMB -> "pull_pin";
                case SPEAR -> "pull_spear";
                case KATANA, LONGSWORD -> "pull_hand";
                case VIOLENCE -> "unmask";
                default -> "";
            };
            run.anim = new AnimSpec(p + "_" + id, "trigger", geo, "", false, AnimSpec.TRANSFORM, run.duration);
        }
    }

    @Override
    public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
        ServerLevel level = player.serverLevel();
        if (run.reverting) {
            if (run.tick == type.revertAt) {
                HybridLogic.revert(player, data);
                if (type == HybridType.CHAINSAW) {
                    Fx.exhaust(level, player.getEyePosition(), 12);
                } else if (type == HybridType.FLAMETHROWER || type == HybridType.BOMB) {
                    Fx.smoke(level, player.getEyePosition(), 8, 0.4);
                } else if (type == HybridType.KATANA || type == HybridType.LONGSWORD) {
                    // sliding the blade back leaves them spent
                    AbilityUtil.sound(player, ModSounds.KATANA_SHEATHE.get(), 1.1f, type == HybridType.KATANA ? 1.1f : 0.8f);
                    player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                            net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
                    player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                            net.minecraft.world.effect.MobEffects.WEAKNESS, 60, 0));
                    data.setCooldown(0, 200);
                } else if (type == HybridType.VIOLENCE) {
                    AbilityUtil.sound(player, ModSounds.VIOLENCE_MASK.get(), 1f, 0.9f);
                    Fx.smoke(level, player.getEyePosition(), 6, 0.2);
                } else if (type == HybridType.COSMOS) {
                    Fx.stars(level, player.getEyePosition(), 16, 0.4);
                } else if (type == HybridType.WHIP) {
                    AbilityUtil.blood(level, AbilityUtil.handPos(player, true, 0.2), 10, 0.15);
                    AbilityUtil.blood(level, AbilityUtil.handPos(player, false, 0.2), 10, 0.15);
                } else {
                    Fx.shards(level, player.getEyePosition(), 6, 0.15);
                }
                AbilityUtil.blood(level, player.getEyePosition(), 8, 0.2);
            }
            return;
        }
        switch (type) {
            case CHAINSAW -> {
                if (run.tick == 8) {
                    AbilityUtil.sound(player, ModSounds.CORD_PULL.get(), 1.0f, 1.0f);
                }
            }
            case CROSSBOW -> {
                if (run.tick == 7) {
                    AbilityUtil.sound(player, ModSounds.ARROW_PULL.get(), 1.0f, 1.0f);
                }
                if (run.tick >= 8 && run.tick <= 18 && run.tick % 2 == 0) {
                    Vec3 eye = player.getEyePosition().add(AbilityUtil.right(player).scale(0.13)).add(player.getLookAngle().scale(0.3));
                    AbilityUtil.blood(level, eye, 3, 0.05);
                }
            }
            case FLAMETHROWER -> {
                if (run.tick == 7) {
                    AbilityUtil.sound(player, ModSounds.MOLAR_CLICK.get(), 1.2f, 1.0f);
                }
            }
            case WHIP -> {
                if (run.tick == 7) {
                    AbilityUtil.sound(player, ModSounds.WHIP_SNAP.get(), 1.3f, 1.0f);
                    Fx.impact(level, AbilityUtil.handPos(player, true, 0.5).add(0, 0.25, 0), 0.6);
                }
            }
            case BOMB -> {
                if (run.tick == 9) {
                    AbilityUtil.sound(player, ModSounds.BOMB_PIN.get(), 1.2f, 1.0f);
                }
                if (!run.failed && run.tick >= 9 && run.tick < type.transformAt) {
                    Fx.fuseSparks(level, player.getEyePosition().add(0, -0.3, 0).add(player.getLookAngle().scale(0.15)), 3);
                    if (run.tick == 10) {
                        AbilityUtil.sound(player, ModSounds.BOMB_FUSE.get(), 0.9f, 1.4f);
                    }
                }
            }
            case KATANA, LONGSWORD -> {
                boolean left = type == HybridType.KATANA;
                if (run.tick == 6) {
                    AbilityUtil.sound(player, left ? ModSounds.KATANA_DRAW.get() : ModSounds.LONGSWORD_DRAW.get(), 1.0f, 1.0f);
                    AbilityUtil.sound(player, ModSounds.HEART_RIP.get(), 0.7f, 1.4f);
                }
                if (run.tick >= 6 && run.tick <= 11 && run.tick % 2 == 0) {
                    AbilityUtil.blood(level, AbilityUtil.handPos(player, !left, 0.1).add(0, -0.3, 0), 5, 0.06);
                }
            }
            case BLOOD -> {
                if (run.tick == 4 || run.tick == 7) {
                    AbilityUtil.sound(player, ModSounds.BLOOD_DRINK.get(), 1.0f, 1.1f);
                }
            }
            case SHARK -> {
                if (run.tick == 5) {
                    AbilityUtil.sound(player, ModSounds.SHARK_BITE.get(), 0.8f, 1.3f);
                }
            }
            case VIOLENCE -> {
                if (run.tick == 8) {
                    AbilityUtil.sound(player, ModSounds.VIOLENCE_MASK.get(), 1.2f, 1.0f);
                }
                if (run.tick >= 8 && run.tick <= 11) {
                    Fx.smoke(level, player.getEyePosition().add(player.getLookAngle().scale(0.4)), 2, 0.1);
                }
            }
            case COSMOS -> {
                if (run.tick == 4) {
                    AbilityUtil.sound(player, ModSounds.COSMOS_HALLOWEEN.get(), 1.0f, 1.0f);
                }
                if (run.tick % 2 == 0) {
                    Fx.stars(level, player.getEyePosition().add(0, 0.3, 0), 3, 0.3);
                }
            }
            case GUN -> {
                if (run.tick == 5) {
                    AbilityUtil.sound(player, ModSounds.GUN_COCK.get(), 1.2f, 0.8f);
                }
            }
            case SPEAR -> {
                if (run.tick == 7) {
                    AbilityUtil.sound(player, ModSounds.SPEAR_PULL.get(), 1.0f, 1.0f);
                }
                if (run.tick >= 8 && run.tick <= 16 && run.tick % 2 == 0) {
                    Vec3 nape = player.getEyePosition().add(0, -0.25, 0).subtract(player.getLookAngle().multiply(1, 0, 1).scale(0.25));
                    AbilityUtil.blood(level, nape, 3, 0.05);
                }
            }
            default -> {
            }
        }
        if (run.tick == type.transformAt) {
            if (run.failed) {
                fail(player, level);
            } else {
                data.addBlood(-TRANSFORM_COST);
                HybridLogic.transform(player, data);
                burst(player, data, level);
            }
        }
    }

    private void fail(ServerPlayer player, ServerLevel level) {
        Vec3 c = player.position().add(0, 1.2, 0);
        if (type == HybridType.CHAINSAW) {
            AbilityUtil.sound(player, ModSounds.CHAINSAW_SPUTTER.get(), 1.0f, 1.0f);
            Fx.exhaust(level, player.getEyePosition(), 14);
        } else if (type == HybridType.BOMB && BombAbilities.tooWet(player)) {
            // the Bomb Devil cannot go off while she is wet
            AbilityUtil.sound(player, SoundEvents.FIRE_EXTINGUISH, 0.8f, 1.2f);
            Fx.smoke(level, player.getEyePosition(), 6, 0.2);
            player.displayClientMessage(Component.translatable("msg.csm.too_wet").withStyle(ChatFormatting.AQUA), true);
            return;
        } else {
            AbilityUtil.sound(player, SoundEvents.FIRE_EXTINGUISH, 0.6f, 1.4f);
            Fx.smoke(level, c.add(0, 0.5, 0), 6, 0.2);
        }
        player.displayClientMessage(Component.translatable("msg.csm.trigger_failed." + type.id).withStyle(ChatFormatting.RED), true);
    }

    /** The moment the devil bursts out of the body. */
    private void burst(ServerPlayer player, HybridData data, ServerLevel level) {
        Vec3 head = player.getEyePosition();
        Vec3 look = player.getLookAngle();
        switch (type) {
            case CHAINSAW -> {
                AbilityUtil.sound(player, ModSounds.CHAINSAW_START.get(), 1.4f, 1.0f);
                AbilityUtil.blood(level, head.add(look.scale(0.35)), 45, 0.25);
                Fx.bloodSpray(level, head.add(look.scale(0.4)), look, 30, 0.55);
                Fx.bloodSpray(level, AbilityUtil.handPos(player, true, 0.0), AbilityUtil.right(player), 18, 0.4);
                Fx.bloodSpray(level, AbilityUtil.handPos(player, false, 0.0), AbilityUtil.right(player).scale(-1), 18, 0.4);
                Fx.sparks(level, head.add(look.scale(0.5)), look, 16, 0.5);
                Fx.impact(level, head.add(look.scale(0.6)), 2.2);
                Fx.shockwave(level, player.position(), 3.5, Fx.BLOOD_RING);
                Fx.exhaust(level, head.add(0, 0.3, 0), 10);
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 1, 0), 2.3)) {
                    AbilityUtil.hurt(player, e, 4f);
                    AbilityUtil.push(e, player.position(), 0.6, 0.25);
                }
            }
            case CROSSBOW -> {
                AbilityUtil.sound(player, ModSounds.TRANSFORM.get(), 1.0f, 1.25f);
                Fx.shards(level, head, 24, 0.35);
                Fx.impact(level, head.add(look.scale(0.5)), 2.0);
                Fx.shockwave(level, player.position(), 3.0, Fx.STEEL_RING);
                AbilityUtil.blood(level, head.add(look.scale(0.3)), 20, 0.15);
            }
            case FLAMETHROWER -> {
                AbilityUtil.sound(player, ModSounds.FLAME_IGNITE.get(), 1.4f, 0.9f);
                Fx.fireBurst(level, player.position().add(0, 0.6, 0), 48, 0.35);
                Fx.fireJet(level, head.add(0, 0.4, 0), new Vec3(0, 1, 0), 20, 0.3, 0.35);
                Fx.embers(level, head, 20, 0.5);
                Fx.shockwave(level, player.position(), 4.0, Fx.FIRE_RING);
                Fx.impact(level, head, 2.0);
                // pressing the molar restores him to peak condition
                player.setHealth(player.getMaxHealth());
                player.clearFire();
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 1, 0), 2.6)) {
                    e.setSecondsOnFire(4);
                }
            }
            case WHIP -> {
                AbilityUtil.sound(player, ModSounds.WHIP_CRACK.get(), 1.5f, 0.8f);
                Vec3 right = AbilityUtil.right(player);
                for (boolean r : new boolean[]{true, false}) {
                    Vec3 hand = AbilityUtil.handPos(player, r, 0.1);
                    Vec3 out = right.scale(r ? 1 : -1);
                    AbilityUtil.blood(level, hand, 22, 0.15);
                    Fx.bloodSpray(level, hand, out.add(0, -0.3, 0), 14, 0.4);
                    Fx.whipArc(level, hand, out.add(look.scale(0.6)), new Vec3(0, 1, 0), 2.2, 0.5);
                    Fx.slash(level, hand.add(out.scale(1.2)), out, 1.4);
                }
                AbilityUtil.blood(level, head.add(look.scale(0.3)), 18, 0.15);
                Fx.impact(level, head.add(look.scale(0.6)), 1.8);
                Fx.shockwave(level, player.position(), 3.2, Fx.BLOOD_RING);
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 1, 0), 3.0)) {
                    AbilityUtil.hurt(player, e, 5f);
                    AbilityUtil.push(e, player.position(), 0.5, 0.2);
                }
            }
            case BOMB -> {
                // pulling the pin: Reze goes off right where she stands, and comes out of the fireball as the Bomb Devil
                Blast.detonate(level, player, null, player.position().add(0, 1.0, 0), 3.5f, 6f, false);
                AbilityUtil.blood(level, head.add(0, -0.3, 0), 20, 0.15);
            }
            case KATANA, LONGSWORD -> {
                boolean left = type == HybridType.KATANA;
                AbilityUtil.sound(player, left ? ModSounds.KATANA_IAI.get() : ModSounds.LONGSWORD_CLEAVE.get(), 1.3f, 0.9f);
                Vec3 right = AbilityUtil.right(player);
                for (boolean r : new boolean[]{true, false}) {
                    Vec3 hand = AbilityUtil.handPos(player, r, 0.1);
                    AbilityUtil.blood(level, hand, 20, 0.15);
                    Fx.bloodSpray(level, hand, right.scale(r ? 1 : -1).add(0, 0.4, 0), 12, 0.4);
                    Fx.sparks(level, hand, look, 8, 0.4);
                }
                Fx.slash(level, head.add(look.scale(1.4)).add(0, -0.3, 0), look.add(0, 0.8, 0), 1.1);
                Fx.impact(level, head.add(look.scale(0.5)), 1.8);
                Fx.shockwave(level, player.position(), 3.0, Fx.STEEL_RING);
            }
            case BLOOD -> {
                AbilityUtil.sound(player, ModSounds.BLOOD_FORM.get(), 1.4f, 0.7f);
                AbilityUtil.blood(level, head.add(0, 0.4, 0), 40, 0.3);
                Fx.bloodSpray(level, head.add(0, 0.5, 0), new Vec3(0, 1, 0), 24, 0.5);
                Fx.shockwave(level, player.position(), 3.5, Fx.BLOOD_RING);
                Fx.impact(level, head, 1.6);
                player.heal(6f);
            }
            case SHARK -> {
                AbilityUtil.sound(player, ModSounds.SHARK_BITE.get(), 1.5f, 0.6f);
                AbilityUtil.sound(player, ModSounds.TRANSFORM.get(), 1.0f, 0.7f);
                AbilityUtil.blood(level, head, 30, 0.3);
                Fx.impact(level, head.add(look.scale(0.6)), 2.0);
                Fx.shockwave(level, player.position(), 3.0, Fx.BLOOD_RING);
            }
            case VIOLENCE -> {
                // the poison-leaking mask comes off and he swells to his real size
                AbilityUtil.sound(player, ModSounds.VIOLENCE_PUNCH.get(), 1.4f, 0.5f);
                AbilityUtil.sound(player, ModSounds.TRANSFORM.get(), 1.0f, 0.6f);
                Fx.impact(level, head, 2.4);
                Fx.shockwave(level, player.position(), 4.0, Fx.STEEL_RING);
                Fx.smoke(level, head, 10, 0.4);
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 1, 0), 3.0)) {
                    AbilityUtil.push(e, player.position(), 1.0, 0.3);
                }
            }
            case COSMOS -> {
                AbilityUtil.sound(player, ModSounds.COSMOS_VOID.get(), 1.4f, 0.8f);
                Fx.stars(level, head.add(0, 0.3, 0), 60, 1.0);
                Fx.halloween(level, head.add(0, 0.8, 0));
                Fx.impact(level, head, 1.4);
            }
            case GUN -> {
                AbilityUtil.sound(player, ModSounds.GUN_CANNON.get(), 1.5f, 0.8f);
                for (int i = 0; i < 6; i++) {
                    Vec3 dir = new Vec3(level.random.nextGaussian() * 0.4, 1, level.random.nextGaussian() * 0.4);
                    Fx.bullet(level, head.add(dir.scale(0.3)), head.add(dir.normalize().scale(24)));
                }
                Fx.sparks(level, head, new Vec3(0, 1, 0), 20, 0.4);
                Fx.smoke(level, head, 8, 0.3);
                Fx.shockwave(level, player.position(), 3.0, Fx.STEEL_RING);
            }
            case SPEAR -> {
                AbilityUtil.sound(player, ModSounds.TRANSFORM.get(), 1.0f, 0.8f);
                Vec3 nape = head.add(0, -0.2, 0).subtract(look.multiply(1, 0, 1).scale(0.3));
                AbilityUtil.blood(level, nape, 30, 0.2);
                Fx.bloodSpray(level, nape, new Vec3(0, 1, 0), 16, 0.4);
                Fx.shards(level, head, 20, 0.3);
                Fx.impact(level, head.add(look.scale(0.5)), 2.0);
                Fx.shockwave(level, player.position(), 3.0, Fx.STEEL_RING);
            }
            default -> {
                if (type.devil) {
                    com.csm.hybrids.ability.devil.DevilMoves.onManifest(player, type);
                }
            }
        }
    }
}
