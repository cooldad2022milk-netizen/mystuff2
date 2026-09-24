package com.csm.hybrids.client.render;

import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import com.csm.hybrids.CsmMod;
import net.minecraft.world.entity.Entity;

/** For entities that are drawn purely with particles (Reze's flicked spark). */
public class NoRenderer<T extends Entity> extends EntityRenderer<T> {
    public NoRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
    }

    @Override
    public boolean shouldRender(T entity, Frustum frustum, double x, double y, double z) {
        return false;
    }

    @Override
    public ResourceLocation getTextureLocation(T entity) {
        return CsmMod.id("textures/misc/none.png");
    }
}
