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
 * What is left of a devil. Hold Use and let it in: you die, and the devil takes your corpse over and walks around in
 * it as a fiend. Whatever was living in you before comes back out as an item.
 */
public class FiendRemainsItem extends HeartItem {
    /** Tick of the use animation where the body gives out. */
    public static final int DEATH_TICK = 18;
    /** Tick where the devil jerks the corpse back up. */
    public static final int RISE_TICK = 34;
    private final HybridType type;

    public FiendRemainsItem(HybridType type, Properties props) {
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
        return "fiend_possession";
    }

    @Override
    protected String doneMessage() {
        return "msg.csm.possessed.";
    }

    @Override
    public void onUseTick(Level level, LivingEntity entity, ItemStack stack, int remaining) {
        if (!(entity instanceof ServerPlayer player)) {
            return;
        }
        int used = getUseDuration(stack) - remaining;
        ServerLevel sl = player.serverLevel();
        Vec3 head = player.getEyePosition();
        if (used == 1) {
            AbilityUtil.sound(player, ModSounds.FIEND_POSSESS.get(), 1.2f, 1f);
        }
        if (used < DEATH_TICK && used % 5 == 0) {
            // the devil worms its way in: the host chokes up blood
            AbilityUtil.blood(sl, head.add(player.getLookAngle().scale(0.3)).add(0, -0.2, 0), 4, 0.06);
        }
        if (used == DEATH_TICK) {
            // the host dies
            AbilityUtil.blood(sl, head, 40, 0.25);
            Fx.bloodSpray(sl, head, player.getLookAngle(), 16, 0.3);
            float dmg = Math.min(8f, player.getHealth() - 1f);
            if (dmg > 0) {
                player.hurt(player.damageSources().generic(), dmg);
            }
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.BLINDNESS, 30, 0, false, false)));
            AbilityUtil.sound(player, ModSounds.HEART_BEAT.get(), 1.4f, 0.5f);
        }
        if (used == RISE_TICK) {
            // ...and the devil stands the corpse back up
            AbilityUtil.sound(player, ModSounds.TRANSFORM.get(), 1.1f, 0.7f);
            Fx.shockwave(sl, player.position(), 2.6, Fx.BLOOD_RING);
            AbilityUtil.blood(sl, head, 20, 0.3);
        }
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        ItemStack out = super.finishUsingItem(stack, level, entity);
        if (entity instanceof ServerPlayer player) {
            player.setHealth(player.getMaxHealth());
            player.removeEffect(MobEffects.BLINDNESS);
        }
        return out;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.csm.remains." + type.id).withStyle(ChatFormatting.DARK_RED));
        tooltip.add(Component.translatable("tooltip.csm.remains_use").withStyle(ChatFormatting.GRAY));
    }
}
