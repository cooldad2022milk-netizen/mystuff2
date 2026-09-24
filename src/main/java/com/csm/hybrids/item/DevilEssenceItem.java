package com.csm.hybrids.item;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * What a slain devil leaves behind. Hold Use and swallow it: the devil pours into you and you become it - a full
 * devil, not a hybrid or a fiend. Whatever was living in you before comes back out as an item.
 */
public class DevilEssenceItem extends HeartItem {
    /** Tick where the devil floods in (the body seizes up). */
    public static final int SEIZE_TICK = 20;
    /** Tick where the devil opens its new eyes. */
    public static final int WAKE_TICK = 40;
    private final HybridType type;

    public DevilEssenceItem(HybridType type, Properties props) {
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
    protected String useAnim() {
        return "devil_consume";
    }

    @Override
    protected String doneMessage() {
        return "msg.csm.became_devil.";
    }

    @Override
    public void onUseTick(Level level, LivingEntity entity, ItemStack stack, int remaining) {
        if (!(entity instanceof ServerPlayer player)) {
            return;
        }
        int used = getUseDuration(stack) - remaining;
        ServerLevel sl = player.serverLevel();
        Vec3 mouth = player.getEyePosition().add(player.getLookAngle().scale(0.3)).add(0, -0.15, 0);
        if (used == 4) {
            AbilityUtil.sound(player, ModSounds.FIEND_POSSESS.get(), 1.0f, 0.8f);
        }
        if (used < SEIZE_TICK && used % 3 == 0) {
            // swallowing it down: dark motes drawn into the mouth
            Fx.smoke(sl, mouth.add(player.getLookAngle().scale(0.4)), 2, 0.12);
        }
        if (used == SEIZE_TICK) {
            AbilityUtil.sound(player, ModSounds.HEART_BEAT.get(), 1.5f, 0.45f);
            AbilityUtil.blood(sl, mouth, 24, 0.2);
            Fx.shockwave(sl, player.position(), 2.4, Fx.BLOOD_RING);
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 40, 0, false, false)));
        }
        if (used > SEIZE_TICK && used < WAKE_TICK && used % 4 == 0) {
            AbilityUtil.blood(sl, player.position().add(0, 1.0, 0), 6, 0.3);
        }
        if (used == WAKE_TICK) {
            AbilityUtil.sound(player, ModSounds.TRANSFORM.get(), 1.2f, 0.55f);
            Fx.shockwave(sl, player.position(), 3.4, Fx.BLOOD_RING);
            Fx.smoke(sl, player.position().add(0, 1, 0), 18, 0.6);
        }
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        ItemStack out = super.finishUsingItem(stack, level, entity);
        if (entity instanceof ServerPlayer player) {
            player.setHealth(player.getMaxHealth());
            player.removeEffect(MobEffects.DARKNESS);
        }
        return out;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.csm.essence." + type.id).withStyle(ChatFormatting.DARK_RED));
        tooltip.add(Component.translatable("tooltip.csm.essence_use").withStyle(ChatFormatting.GRAY));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }
}
