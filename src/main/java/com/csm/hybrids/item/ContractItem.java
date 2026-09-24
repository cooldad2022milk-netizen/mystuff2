package com.csm.hybrids.item;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.contract.Contract;
import com.csm.hybrids.contract.Contracts;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.network.AnimSpec;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * A devil's contract. Hold Use: bite your thumb and seal it in blood. The devil takes its price and from then on
 * you can call on it (the contract's moves join your ability wheel). Anyone can hold contracts, and several at once.
 */
public class ContractItem extends Item {
    public static final int USE_TICKS = 40;
    /** Tick where the thumb is pressed to the paper. */
    public static final int SEAL_TICK = 22;
    private final Contract contract;

    public ContractItem(Contract contract, Properties props) {
        super(props);
        this.contract = contract;
    }

    public Contract contract() {
        return contract;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        HybridData data = HybridCapability.get(player);
        if (data == null || data.activeRun != null) {
            return InteractionResultHolder.fail(stack);
        }
        if (data.hasContract(contract)) {
            if (!level.isClientSide) {
                player.displayClientMessage(Component.translatable("msg.csm.contract_already")
                        .withStyle(ChatFormatting.GRAY), true);
            }
            return InteractionResultHolder.fail(stack);
        }
        player.startUsingItem(hand);
        if (player instanceof ServerPlayer sp) {
            HybridLogic.broadcastAnim(sp, new AnimSpec("contract_sign", "", "", "", false, AnimSpec.HEART, USE_TICKS));
        }
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void onUseTick(Level level, LivingEntity entity, ItemStack stack, int remaining) {
        if (!(entity instanceof ServerPlayer player)) {
            return;
        }
        int used = getUseDuration(stack) - remaining;
        ServerLevel sl = player.serverLevel();
        Vec3 hand = player.getEyePosition().add(player.getLookAngle().scale(0.45)).add(0, -0.35, 0);
        if (used == 8) {
            // bite the thumb
            AbilityUtil.sound(player, ModSounds.DEVIL_BITE.get(), 0.5f, 1.8f);
            AbilityUtil.blood(sl, player.getEyePosition().add(player.getLookAngle().scale(0.3)).add(0, -0.2, 0), 6, 0.05);
        }
        if (used == SEAL_TICK) {
            AbilityUtil.sound(player, ModSounds.HEART_BEAT.get(), 1.3f, 0.5f);
            AbilityUtil.blood(sl, hand, 12, 0.08);
            Fx.smoke(sl, hand, 6, 0.3);
        }
        if (used > SEAL_TICK && used % 5 == 0) {
            Fx.smoke(sl, hand, 2, 0.4);
        }
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (entity instanceof ServerPlayer player) {
            HybridData data = HybridCapability.get(player);
            if (data != null && Contracts.sign(player, data, contract) && !player.getAbilities().instabuild) {
                stack.shrink(1);
            }
        }
        return stack;
    }

    @Override
    public void releaseUsing(ItemStack stack, Level level, LivingEntity entity, int timeLeft) {
        if (entity instanceof ServerPlayer player) {
            HybridLogic.broadcastAnim(player, AnimSpec.stop());
        }
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return USE_TICKS;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.NONE;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.csm.contract." + contract.id).withStyle(ChatFormatting.DARK_RED));
        tooltip.add(Component.translatable("tooltip.csm.contract_price." + contract.id).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.csm.contract_use").withStyle(ChatFormatting.DARK_GRAY));
    }
}
