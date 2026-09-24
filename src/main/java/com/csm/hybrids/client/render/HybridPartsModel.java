package com.csm.hybrids.client.render;

import com.csm.hybrids.CsmMod;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

/** Resolves geo/texture/animation files per hybrid: assets/csm/{geo,textures,animations}/hybrid/<type>.* */
public class HybridPartsModel extends GeoModel<HybridPartsAnimatable> {
    @Override
    public ResourceLocation getModelResource(HybridPartsAnimatable animatable) {
        return CsmMod.id("geo/hybrid/" + animatable.type.id + ".geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(HybridPartsAnimatable animatable) {
        return CsmMod.id("textures/hybrid/" + animatable.type.id + ".png");
    }

    @Override
    public ResourceLocation getAnimationResource(HybridPartsAnimatable animatable) {
        return CsmMod.id("animations/hybrid/" + animatable.type.id + ".animation.json");
    }
}
