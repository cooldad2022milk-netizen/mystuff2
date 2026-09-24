package com.csm.hybrids.client.render;

import com.csm.hybrids.client.ClientHybridState;
import com.csm.hybrids.hybrid.HybridType;
import com.mojang.blaze3d.vertex.PoseStack;
import dev.kosmx.playerAnim.api.firstPerson.FirstPersonMode;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.PlayerItemInHandLayer;

/**
 * Player render layer that draws the hybrid's devil parts on top of the vanilla model.
 * <p>
 * It extends {@link PlayerItemInHandLayer} on purpose: during PlayerAnimator's first-person pass (moves played
 * with {@code FirstPersonMode.THIRD_PERSON_MODEL}) every layer except item-in-hand layers is filtered out, which
 * made the devil arms vanish in first person while a move was playing. It never draws items itself.
 */
public class HybridFormLayer extends PlayerItemInHandLayer<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> {
    public HybridFormLayer(RenderLayerParent<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> parent,
                           ItemInHandRenderer itemInHandRenderer) {
        super(parent, itemInHandRenderer);
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource buffers, int light, AbstractClientPlayer player,
                       float limbSwing, float limbSwingAmount, float partialTick, float ageInTicks, float netHeadYaw,
                       float headPitch) {
        if (player.isInvisible() || player.isSpectator()) {
            return;
        }
        ClientHybridState state = ClientHybridState.of(player);
        if (state == null || state.type == HybridType.NONE || state.type.monster()) {
            return;
        }
        HybridPartRenderer.get().renderOnPlayer(poseStack, buffers, light, player, getParentModel(), state, partialTick,
                FirstPersonMode.isFirstPersonPass(), null);
    }
}
