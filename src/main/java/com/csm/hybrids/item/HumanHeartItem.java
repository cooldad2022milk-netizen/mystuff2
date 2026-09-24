package com.csm.hybrids.item;

import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Your original heart. Putting it back turns a hybrid human again and returns the devil's heart. */
public class HumanHeartItem extends HeartItem {
    public HumanHeartItem(Properties props) {
        super(props);
    }

    @Override
    protected HybridType resultType() {
        return HybridType.NONE;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.csm.human_heart").withStyle(ChatFormatting.GRAY));
    }
}
