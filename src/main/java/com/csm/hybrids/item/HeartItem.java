package com.csm.hybrids.item;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.network.AnimSpec;
import com.csm.hybrids.registry.ModItems;
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
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Hold use to perform a heart replacement: rip your own heart out of your chest and push this one in.
 * Whatever heart was beating in there before comes back out as an item.
 */
public abstract class HeartItem extends Item {
    public static final int USE_TICKS = 50;
    /** Tick of the use animation where the old heart is torn out. */
    public static final int RIP_TICK = 22;

    protected HeartItem(Properties props) {
        super(props);
    }

    /** The hybrid the player becomes after putting this heart in. */
    protected abstract HybridType resultType();

    /** Body animation played while the item is used. */
    protected String useAnim() {
        return "heart_replace";
    }

    /** Chat message shown once the swap is done (suffixed with the new type's id). */
    protected String doneMessage() {
        return "msg.csm.heart_replaced.";
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        HybridData data = HybridCapability.get(player);
        if (data == null) {
            return InteractionResultHolder.pass(stack);
        }
        if (data.type() == resultType()) {
            if (!level.isClientSide) {
                player.displayClientMessage(Component.translatable(resultType() == HybridType.NONE
                        ? "msg.csm.already_human" : "msg.csm.same_heart").withStyle(ChatFormatting.GRAY), true);
            }
            return InteractionResultHolder.fail(stack);
        }
        if (data.activeRun != null) {
            return InteractionResultHolder.fail(stack);
        }
        player.startUsingItem(hand);
        if (player instanceof ServerPlayer sp) {
            HybridLogic.broadcastAnim(sp, new AnimSpec(useAnim(), "", "", "", false, AnimSpec.HEART, USE_TICKS));
            AbilityUtil.sound(sp, ModSounds.HEART_BEAT.get(), 1f, 1f);
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
        Vec3 chest = player.position().add(0, 1.25, 0).add(player.getLookAngle().multiply(0.35, 0, 0.35));
        if (used == RIP_TICK) {
            AbilityUtil.sound(player, ModSounds.HEART_RIP.get(), 1.2f, 1f);
            AbilityUtil.blood(sl, chest, 50, 0.25);
            float dmg = Math.min(6f, player.getHealth() - 1f);
            if (dmg > 0) {
                player.hurt(player.damageSources().generic(), dmg);
            }
        } else if (used > RIP_TICK && used % 4 == 0) {
            AbilityUtil.blood(sl, chest, 6, 0.12);
        } else if (used % 10 == 0) {
            AbilityUtil.sound(player, ModSounds.HEART_BEAT.get(), 0.6f, 1f + used / 80f);
        }
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (entity instanceof ServerPlayer player) {
            HybridData data = HybridCapability.get(player);
            if (data != null && data.type() != resultType()) {
                HybridType old = data.type();
                HybridLogic.setType(player, data, resultType());
                ItemStack removed = new ItemStack(old == HybridType.NONE ? ModItems.HUMAN_HEART.get() : ModItems.heartFor(old));
                if (!player.getInventory().add(removed)) {
                    player.drop(removed, false);
                }
                AbilityUtil.sound(player, ModSounds.HEART_BEAT.get(), 1.4f, 0.7f);
                player.displayClientMessage(Component.translatable(doneMessage() + resultType().id)
                        .withStyle(ChatFormatting.DARK_RED), false);
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
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
}
