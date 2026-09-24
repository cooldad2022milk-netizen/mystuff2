package com.csm.hybrids.item;

import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** A devil's heart. Replace your own heart with it to become that devil's hybrid. */
public class DevilHeartItem extends HeartItem {
    private final HybridType type;

    public DevilHeartItem(HybridType type, Properties props) {
        super(props);
        this.type = type;
    }

    public HybridType type() {
        return type;
    }

    @Override
    protected HybridType resultType() {
        return type;
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return false;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.csm.devil_heart." + type.id).withStyle(ChatFormatting.DARK_RED));
        tooltip.add(Component.translatable("tooltip.csm.heart_use").withStyle(ChatFormatting.GRAY));
    }
}
