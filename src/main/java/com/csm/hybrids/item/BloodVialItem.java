package com.csm.hybrids.item;

import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUtils;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * Blood bottled from a living creature (use an empty glass bottle on a mob).
 * Hybrids drink it to refill their blood; for humans it's just gross.
 */
public class BloodVialItem extends Item {
    public BloodVialItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        return ItemUtils.startUsingInstantly(level, player, hand);
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        if (entity instanceof ServerPlayer player) {
            HybridData data = HybridCapability.get(player);
            if (data != null && data.isHybrid()) {
                HybridLogic.addBlood(player, 25f);
                player.heal(2f);
                HybridLogic.sync(player, data);
            } else {
                player.addEffect(com.csm.hybrids.ability.AbilityUtil.quiet(new MobEffectInstance(MobEffects.CONFUSION, 160)));
                player.displayClientMessage(Component.translatable("msg.csm.blood_gross").withStyle(ChatFormatting.GRAY), true);
            }
            level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.BLOOD_DRINK.get(), SoundSource.PLAYERS, 1f, 1f);
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
                ItemStack bottle = new ItemStack(Items.GLASS_BOTTLE);
                if (stack.isEmpty()) {
                    return bottle;
                }
                if (!player.getInventory().add(bottle)) {
                    player.drop(bottle, false);
                }
            }
        }
        return stack;
    }

    @Override
    public int getUseDuration(ItemStack stack) {
        return 24;
    }

    @Override
    public UseAnim getUseAnimation(ItemStack stack) {
        return UseAnim.DRINK;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.csm.blood_vial").withStyle(ChatFormatting.GRAY));
    }
}
