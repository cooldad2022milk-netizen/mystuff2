package com.csm.hybrids.effect;

import com.csm.hybrids.registry.ModParticles;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * Cosmo's power: the victim is forced to understand the entire universe at once and can't think anything but
 * "Halloween". Mobs stand frozen, forget their target and stop moving; players crawl along with their screen flooded
 * (see the client overlay). Level 2+ also burns the mind for magic damage every second.
 */
public class HalloweenEffect extends MobEffect {
    public HalloweenEffect() {
        super(MobEffectCategory.HARMFUL, 0xF08CC8);
        addAttributeModifier(Attributes.MOVEMENT_SPEED, "6f1d3f0e-7a55-4c1c-9c4b-2d1f0c11a001", -0.75,
                AttributeModifier.Operation.MULTIPLY_TOTAL);
        addAttributeModifier(Attributes.ATTACK_DAMAGE, "6f1d3f0e-7a55-4c1c-9c4b-2d1f0c11a002", -0.6,
                AttributeModifier.Operation.MULTIPLY_TOTAL);
    }

    @Override
    public boolean isDurationEffectTick(int duration, int amplifier) {
        return true;
    }

    @Override
    public void applyEffectTick(LivingEntity entity, int amplifier) {
        if (entity instanceof Mob mob) {
            mob.getNavigation().stop();
            mob.setTarget(null);
            mob.setDeltaMovement(0, Math.min(mob.getDeltaMovement().y, 0), 0);
            mob.setYRot(mob.yRotO);
        }
        if (entity.level() instanceof ServerLevel level && entity.tickCount % 14 == 0) {
            level.sendParticles(ModParticles.HALLOWEEN.get(), entity.getX(), entity.getEyeY() + 0.6, entity.getZ(), 1,
                    0.25, 0.1, 0.25, 0.0);
            level.sendParticles(ModParticles.STAR.get(), entity.getX(), entity.getEyeY(), entity.getZ(), 3,
                    0.35, 0.3, 0.35, 0.01);
        }
        if (amplifier >= 1 && entity.tickCount % 20 == 0) {
            entity.hurt(entity.damageSources().magic(), 1.0f + amplifier * 0.5f);
        }
    }
}
