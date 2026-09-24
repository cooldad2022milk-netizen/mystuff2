package com.csm.hybrids.effect;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * Wounds the Darkness Devil leaves behind.
 * <ul>
 *   <li>Unhealing: wounds that resist healing (see DevilEvents: every heal is cancelled while it lasts)</li>
 *   <li>Severed: both arms sheared off - you can barely fight and whatever you held is on the floor</li>
 * </ul>
 */
public class DevilWoundEffect extends MobEffect {
    public DevilWoundEffect(int color, boolean severed) {
        super(MobEffectCategory.HARMFUL, color);
        if (severed) {
            addAttributeModifier(Attributes.ATTACK_DAMAGE, "6f1d3f0e-7a55-4c1c-9c4b-2d1f0c11a101", -0.8,
                    AttributeModifier.Operation.MULTIPLY_TOTAL);
            addAttributeModifier(Attributes.ATTACK_SPEED, "6f1d3f0e-7a55-4c1c-9c4b-2d1f0c11a102", -0.6,
                    AttributeModifier.Operation.MULTIPLY_TOTAL);
        }
    }
}
