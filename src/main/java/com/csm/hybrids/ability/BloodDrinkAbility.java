package com.csm.hybrids.ability;

import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Hybrids heal by drinking blood. Bite into whatever is in front of you, or burn stored blood to heal.
 * Works in human form too.
 */
public class BloodDrinkAbility extends Ability {
    public BloodDrinkAbility(HybridType type) {
        super(type, "blood_drink_" + type.id);
        anyForm();
        timing(20, 60);
        anim("blood_drink", "drink");
    }

    @Override
    public net.minecraft.network.chat.Component displayName() {
        return Component.translatable("ability.csm.blood_drink");
    }

    @Override
    public net.minecraft.network.chat.Component description() {
        return Component.translatable("ability.csm.blood_drink.desc");
    }

    @Override
    public net.minecraft.resources.ResourceLocation icon() {
        return com.csm.hybrids.CsmMod.id("textures/gui/ability/blood_drink.png");
    }

    @Override
    public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
        if (run.tick != 10) {
            return;
        }
        EntityHitResult hit = AbilityUtil.raycastEntity(player, 3.5);
        Vec3 mouth = player.getEyePosition().add(player.getLookAngle().scale(0.3)).add(0, -0.15, 0);
        if (hit != null && hit.getEntity() instanceof LivingEntity target) {
            AbilityUtil.hurtIgnoringIFrames(player, target, 4f);
            player.heal(4f);
            HybridLogic.addBlood(player, 18f);
            AbilityUtil.blood(player.serverLevel(), target.getBoundingBox().getCenter(), 30, 0.25);
            AbilityUtil.sound(player, ModSounds.BLOOD_DRINK.get(), 1f, 1f);
        } else if (data.blood() >= 20f) {
            data.addBlood(-20f);
            player.heal(8f);
            AbilityUtil.blood(player.serverLevel(), mouth, 12, 0.08);
            AbilityUtil.sound(player, ModSounds.BLOOD_DRINK.get(), 1f, 0.8f);
        } else {
            player.displayClientMessage(Component.translatable("msg.csm.no_blood_to_drink").withStyle(ChatFormatting.RED), true);
        }
    }
}
