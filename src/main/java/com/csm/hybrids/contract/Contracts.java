package com.csm.hybrids.contract;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.ContractSummonEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.UUID;

/** Making contracts, and the prices that are paid later (the Curse Devil's toll on your lifespan). */
public final class Contracts {
    private static final UUID TOLL_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e09");
    /** The Curse stops taking lifespan once this many hearts are gone (it still comes when called). */
    public static final int MAX_TOLL = 7;

    /**
     * Sign {@code c}: the devil takes its price and the contract is yours.
     *
     * @return false if the player already holds it
     */
    public static boolean sign(ServerPlayer player, HybridData data, Contract c) {
        if (!data.addContract(c)) {
            return false;
        }
        ServerLevel level = player.serverLevel();
        Vec3 chest = player.position().add(0, 1.2, 0);
        switch (c) {
            case FOX_HEAD, FOX_PAW -> {
                // the fox takes its first mouthful of you
                if (!player.getAbilities().instabuild) {
                    player.setHealth(Math.max(1f, player.getHealth() - 4f));
                }
                AbilityUtil.blood(level, chest, 30, 0.3);
                AbilityUtil.sound(player, ModSounds.DEVIL_BITE.get(), 1.0f, 1.3f);
            }
            case CURSE -> AbilityUtil.sound(player, ModSounds.DEVIL_ROAR.get(), 0.7f, 0.5f);
            case FUTURE -> {
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 60, 0, false, false)));
                AbilityUtil.sound(player, ModSounds.COSMOS_HALLOWEEN.get(), 0.9f, 1.5f);
                Fx.stars(level, player.getEyePosition(), 12, 0.3);
            }
            case GHOST -> {
                // it takes your right eye
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.BLINDNESS, 80, 0, false, false)));
                AbilityUtil.blood(level, player.getEyePosition(), 16, 0.1);
                AbilityUtil.sound(player, ModSounds.HEART_RIP.get(), 0.9f, 1.4f);
            }
        }
        player.displayClientMessage(Component.translatable("msg.csm.contract_signed." + c.id)
                .withStyle(ChatFormatting.DARK_RED), false);
        HybridLogic.sync(player, data);
        return true;
    }

    /** Break a contract (commands only: devils don't let go that easily). */
    public static boolean breakContract(ServerPlayer player, HybridData data, Contract c) {
        if (!data.removeContract(c)) {
            return false;
        }
        if (data.activeRun != null && data.activeRun.ability instanceof ContractAbility ca && ca.contract == c) {
            HybridLogic.cancelRun(player, data);
        }
        HybridLogic.sync(player, data);
        return true;
    }

    // ------------------------------------------------------------------ the Curse Devil
    /** The third nail: the Curse Devil manifests behind the victim, and takes a heart of the contractor's lifespan. */
    public static void curseManifest(ServerPlayer player, HybridData data, LivingEntity victim) {
        ServerLevel level = player.serverLevel();
        Vec3 dir = victim.position().subtract(player.position());
        dir = new Vec3(dir.x, 0, dir.z);
        dir = dir.lengthSqr() > 1e-4 ? dir.normalize() : new Vec3(player.getLookAngle().x, 0, player.getLookAngle().z).normalize();
        Vec3 behind = victim.position().add(dir.scale(victim.getBbWidth() * 0.5 + 1.3));
        ContractSummonEntity.summon(level, ContractSummonEntity.Kind.CURSE, player, victim, behind, dir.reverse());
        AbilityUtil.sound(player, ModSounds.DEVIL_ROAR.get(), 1.6f, 0.45f);
        if (!player.getAbilities().instabuild && data.curseToll() < MAX_TOLL) {
            data.setCurseToll(data.curseToll() + 1);
            applyToll(player, data);
            player.displayClientMessage(Component.translatable("msg.csm.curse_toll", data.curseToll())
                    .withStyle(ChatFormatting.DARK_RED), true);
        }
    }

    /** Hearts of lifespan the Curse took are gone for good: max health is lowered by that much. */
    public static void applyToll(ServerPlayer player, HybridData data) {
        AttributeInstance hp = player.getAttribute(Attributes.MAX_HEALTH);
        if (hp == null) {
            return;
        }
        hp.removeModifier(TOLL_ID);
        int toll = Math.min(data.curseToll(), MAX_TOLL);
        if (toll > 0) {
            hp.addTransientModifier(new AttributeModifier(TOLL_ID, "csm_curse_toll", -2.0 * toll,
                    AttributeModifier.Operation.ADDITION));
        }
        if (player.getHealth() > player.getMaxHealth()) {
            player.setHealth(player.getMaxHealth());
        }
    }

    // ------------------------------------------------------------------ aiming
    /** Where a summon lands when nothing is under the crosshair: the block looked at, or the ground ahead. */
    public static Vec3 aimPoint(ServerPlayer player, double range) {
        BlockHitResult block = AbilityUtil.raycastBlock(player, range);
        Vec3 p = block.getType() == HitResult.Type.MISS
                ? player.getEyePosition().add(player.getLookAngle().scale(Math.min(range, 8)))
                : block.getLocation();
        Vec3 ground = AbilityUtil.groundBelow(player.serverLevel(), p, 12);
        return ground != null ? ground : p;
    }

    private Contracts() {
    }
}
