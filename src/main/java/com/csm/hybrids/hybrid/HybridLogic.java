package com.csm.hybrids.hybrid;

import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.config.CsmConfig;
import com.csm.hybrids.devil.DevilSpec;
import com.csm.hybrids.devil.DevilSpecs;
import com.csm.hybrids.network.AnimSpec;
import com.csm.hybrids.network.CsmNetwork;
import com.csm.hybrids.network.PlayAnimPacket;
import com.csm.hybrids.network.SyncHybridPacket;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.ForgeMod;

import java.util.List;
import java.util.UUID;

/**
 * Server-side hybrid rules: using abilities, transforming, blood economy, syncing.
 */
public final class HybridLogic {
    private static final UUID DAMAGE_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e01");
    private static final UUID SPEED_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e02");
    private static final UUID ARMOR_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e03");
    private static final UUID TOUGH_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e04");
    private static final UUID KNOCK_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e05");
    private static final UUID ATK_SPEED_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e06");
    private static final UUID REACH_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e07");
    private static final UUID HEALTH_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e08");

    // ------------------------------------------------------------------ abilities
    public static void tryUseAbility(ServerPlayer player, int index) {
        HybridData data = HybridCapability.get(player);
        if (data == null || !data.hasAbilities() || player.isSpectator() || !player.isAlive()) {
            return;
        }
        List<Ability> abilities = data.abilities();
        if (index < 0 || index >= abilities.size()) {
            return;
        }
        if (data.activeRun != null) {
            return; // mid-action: ignore spam
        }
        Ability ability = abilities.get(index);
        if (data.cooldown(index) > 0) {
            player.displayClientMessage(Component.translatable("msg.csm.cooldown", ability.displayName(),
                    String.format("%.1f", data.cooldown(index) / 20f)).withStyle(ChatFormatting.GRAY), true);
            return;
        }
        String fail = ability.checkUse(player, data);
        if (fail != null) {
            player.displayClientMessage(Component.translatable(fail, ability.displayName()).withStyle(ChatFormatting.RED), true);
            return;
        }
        AbilityRun run = new AbilityRun(ability, index);
        ability.prepare(player, data, run);
        data.activeRun = run;
        if (ability.consumesBloodOnStart()) {
            data.addBlood(-ability.bloodCost());
        }
        data.setCooldown(index, ability.cooldown() + run.duration);
        ability.start(player, data, run);
        broadcastAnim(player, run.anim);
        sync(player, data);
    }

    public static void broadcastAnim(ServerPlayer player, AnimSpec spec) {
        if (spec != null) {
            CsmNetwork.toTrackingAndSelf(player, new PlayAnimPacket(player.getId(), spec));
        }
    }

    public static void cancelRun(ServerPlayer player, HybridData data) {
        if (data.activeRun != null) {
            data.activeRun.ability.end(player, data, data.activeRun);
            data.activeRun = null;
            broadcastAnim(player, AnimSpec.stop());
        }
    }

    public static void tick(ServerPlayer player) {
        HybridData data = HybridCapability.get(player);
        if (data == null) {
            return;
        }
        data.tickCooldowns();
        // moves run for anyone with a wheel (a human contractor too)
        AbilityRun run = data.activeRun;
        if (run != null) {
            if (!player.isAlive()) {
                data.activeRun = null;
            } else {
                run.ability.tick(player, data, run);
                run.tick++;
                if (run.tick >= run.duration) {
                    run.ability.end(player, data, run);
                    if (data.activeRun == run) {
                        data.activeRun = null;
                    }
                }
            }
        }
        if (!data.isHybrid()) {
            if (data.consumeDirty()) {
                sync(player, data);
            }
            return;
        }

        // Hybrids knit their flesh back together by burning the blood they have drunk.
        if (player.tickCount % 20 == 0) {
            if (data.isTransformed()) {
                if (player.getHealth() < player.getMaxHealth() && data.blood() >= 1f) {
                    player.heal(1.5f);
                    data.addBlood(-0.75f);
                }
            } else if (data.blood() < 30f && player.tickCount % 200 == 0) {
                data.addBlood(1f);
            }
        }
        if (data.isTransformed() && data.type() == HybridType.FLAMETHROWER && player.isOnFire()) {
            player.clearFire();
        }
        if (data.consumeDirty() || Math.abs(data.blood() - data.lastSyncedBlood) >= 0.5f) {
            sync(player, data);
        }
    }

    // ------------------------------------------------------------------ form
    public static void transform(ServerPlayer player, HybridData data) {
        if (data.isTransformed()) {
            return;
        }
        data.setTransformed(true);
        applyAttributes(player, data);
        player.refreshDimensions();
        sync(player, data);
    }

    public static void revert(ServerPlayer player, HybridData data) {
        if (!data.isTransformed()) {
            return;
        }
        data.setTransformed(false);
        removeAttributes(player);
        player.refreshDimensions();
        AbilityUtil.sound(player, ModSounds.REVERT.get(), 0.8f, 1.0f);
        sync(player, data);
    }

    /** Heart replacement: become (or stop being) a hybrid. */
    public static void setType(ServerPlayer player, HybridData data, HybridType type) {
        if (data.activeRun != null) {
            cancelRun(player, data);
        }
        if (data.isTransformed()) {
            data.setTransformed(false);
            removeAttributes(player);
        }
        data.setType(type);
        data.setBlood(type == HybridType.NONE ? 0 : CsmConfig.STARTING_BLOOD.get().floatValue());
        player.refreshDimensions();
        sync(player, data);
    }

    public static void applyAttributes(ServerPlayer player, HybridData data) {
        removeAttributes(player);
        switch (data.type()) {
            case CHAINSAW -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 6, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.4, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.15, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 6, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID, 0.3, AttributeModifier.Operation.ADDITION);
            }
            case CROSSBOW -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 4, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.6, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.45, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 4, AttributeModifier.Operation.ADDITION);
            }
            case FLAMETHROWER -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 5, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.08, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 10, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ARMOR_TOUGHNESS, TOUGH_ID, 4, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID, 0.6, AttributeModifier.Operation.ADDITION);
            }
            case WHIP -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 5, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.5, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.3, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 4, AttributeModifier.Operation.ADDITION);
                add(player, ForgeMod.ENTITY_REACH.get(), REACH_ID, 2.5, AttributeModifier.Operation.ADDITION);
            }
            case BOMB -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 5, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.4, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.25, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 6, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID, 0.4, AttributeModifier.Operation.ADDITION);
            }
            case KATANA -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 6, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.6, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.3, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 5, AttributeModifier.Operation.ADDITION);
                add(player, ForgeMod.ENTITY_REACH.get(), REACH_ID, 1.0, AttributeModifier.Operation.ADDITION);
            }
            case LONGSWORD -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 7, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.3, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.15, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 7, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID, 0.3, AttributeModifier.Operation.ADDITION);
                add(player, ForgeMod.ENTITY_REACH.get(), REACH_ID, 1.5, AttributeModifier.Operation.ADDITION);
            }
            case BLOOD -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 5, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.2, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 4, AttributeModifier.Operation.ADDITION);
            }
            case SHARK -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 6, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.25, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 6, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID, 0.3, AttributeModifier.Operation.ADDITION);
            }
            case VIOLENCE -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 10, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.3, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.1, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 8, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ARMOR_TOUGHNESS, TOUGH_ID, 4, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID, 0.8, AttributeModifier.Operation.ADDITION);
                add(player, ForgeMod.ENTITY_REACH.get(), REACH_ID, 1.0, AttributeModifier.Operation.ADDITION);
            }
            case COSMOS -> {
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.1, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 3, AttributeModifier.Operation.ADDITION);
            }
            case GUN -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 3, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.1, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 5, AttributeModifier.Operation.ADDITION);
            }
            case SPEAR -> {
                add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, 7, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID, 0.3, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, 0.2, AttributeModifier.Operation.MULTIPLY_BASE);
                add(player, Attributes.ARMOR, ARMOR_ID, 8, AttributeModifier.Operation.ADDITION);
                add(player, Attributes.ARMOR_TOUGHNESS, TOUGH_ID, 2, AttributeModifier.Operation.ADDITION);
                add(player, ForgeMod.ENTITY_REACH.get(), REACH_ID, 1.5, AttributeModifier.Operation.ADDITION);
            }
            default -> {
                if (data.type().devil) {
                    devilAttributes(player, DevilSpecs.of(data.type()));
                }
            }
        }
    }

    /** A full devil's form: tougher and stronger in proportion to the devil (and able to fly if it can). */
    private static void devilAttributes(ServerPlayer player, DevilSpec spec) {
        add(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID, spec.formDamage, AttributeModifier.Operation.ADDITION);
        add(player, Attributes.MOVEMENT_SPEED, SPEED_ID, spec.formSpeed, AttributeModifier.Operation.MULTIPLY_BASE);
        add(player, Attributes.ARMOR, ARMOR_ID, spec.formArmor, AttributeModifier.Operation.ADDITION);
        add(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID, spec.formKnockback, AttributeModifier.Operation.ADDITION);
        add(player, Attributes.MAX_HEALTH, HEALTH_ID, spec.formHealth, AttributeModifier.Operation.ADDITION);
        if (spec.resizesPlayer()) {
            add(player, ForgeMod.ENTITY_REACH.get(), REACH_ID, Math.max(0, spec.playerHeight - 1.8) * 0.8,
                    AttributeModifier.Operation.ADDITION);
        }
        if (spec.flying && !player.getAbilities().mayfly) {
            player.getAbilities().mayfly = true;
            player.getPersistentData().putBoolean("csm_devil_flight", true);
            player.onUpdateAbilities();
        }
    }

    public static void removeAttributes(ServerPlayer player) {
        remove(player, Attributes.ATTACK_DAMAGE, DAMAGE_ID);
        remove(player, Attributes.ATTACK_SPEED, ATK_SPEED_ID);
        remove(player, Attributes.MOVEMENT_SPEED, SPEED_ID);
        remove(player, Attributes.ARMOR, ARMOR_ID);
        remove(player, Attributes.ARMOR_TOUGHNESS, TOUGH_ID);
        remove(player, Attributes.KNOCKBACK_RESISTANCE, KNOCK_ID);
        remove(player, ForgeMod.ENTITY_REACH.get(), REACH_ID);
        remove(player, Attributes.MAX_HEALTH, HEALTH_ID);
        if (player.getHealth() > player.getMaxHealth()) {
            player.setHealth(player.getMaxHealth());
        }
        if (player.getPersistentData().getBoolean("csm_devil_flight")) {
            player.getPersistentData().remove("csm_devil_flight");
            if (!player.isCreative() && !player.isSpectator()) {
                player.getAbilities().mayfly = false;
                player.getAbilities().flying = false;
                player.onUpdateAbilities();
            }
        }
    }

    private static void add(ServerPlayer p, Attribute attr, UUID id, double amount, AttributeModifier.Operation op) {
        AttributeInstance inst = p.getAttribute(attr);
        if (inst != null && inst.getModifier(id) == null) {
            inst.addTransientModifier(new AttributeModifier(id, "csm_hybrid_form", amount, op));
        }
    }

    private static void remove(ServerPlayer p, Attribute attr, UUID id) {
        AttributeInstance inst = p.getAttribute(attr);
        if (inst != null) {
            inst.removeModifier(id);
        }
    }

    // ------------------------------------------------------------------ blood
    public static void addBlood(ServerPlayer player, float amount) {
        HybridData data = HybridCapability.get(player);
        if (data != null && data.isHybrid()) {
            data.addBlood(amount * CsmConfig.BLOOD_GAIN_MULTIPLIER.get().floatValue());
        }
    }

    /**
     * A hybrid only truly dies if their heart stops. With enough blood in the tank the devil heart
     * drags them back (Barem: "as long as someone presses the molar, he comes back").
     */
    public static boolean tryRevive(ServerPlayer player, HybridData data) {
        float cost = CsmConfig.REVIVE_BLOOD_COST.get().floatValue();
        if (!data.isHybrid() || cost > HybridData.MAX_BLOOD || data.blood() < cost) {
            return false;
        }
        data.addBlood(-cost);
        if (data.activeRun != null) {
            cancelRun(player, data);
        }
        if (data.isTransformed()) {
            data.setTransformed(false);
            removeAttributes(player);
        }
        player.setHealth(Math.max(4f, player.getMaxHealth() * 0.3f));
        player.removeAllEffects();
        player.clearFire();
        player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.REGENERATION, 100, 1)));
        player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 60, 2)));
        ServerLevel level = player.serverLevel();
        Vec3 c = player.position().add(0, 1.1, 0);
        AbilityUtil.blood(level, c, 60, 0.6);
        Fx.impact(level, c, 2.4);
        Fx.shockwave(level, player.position(), 3.0, Fx.BLOOD_RING);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.HEART_BEAT.get(), SoundSource.PLAYERS, 1.2f, 0.8f);
        player.displayClientMessage(Component.translatable("msg.csm.revived." + data.type().id).withStyle(ChatFormatting.DARK_RED), true);
        sync(player, data);
        return true;
    }

    // ------------------------------------------------------------------ sync
    public static void sync(ServerPlayer player, HybridData data) {
        data.lastSyncedBlood = data.blood();
        CsmNetwork.toPlayer(player, SyncHybridPacket.of(player.getId(), data, true));
        CsmNetwork.toTracking(player, SyncHybridPacket.of(player.getId(), data, false));
    }

    public static void syncTo(ServerPlayer target, ServerPlayer viewer) {
        HybridData data = HybridCapability.get(target);
        if (data != null) {
            CsmNetwork.toPlayer(viewer, SyncHybridPacket.of(target.getId(), data, target == viewer));
        }
    }

    private HybridLogic() {
    }
}
