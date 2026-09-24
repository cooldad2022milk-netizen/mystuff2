package com.csm.hybrids.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Server -> clients: player {@code entityId} starts an action (body + devil-part animations). */
public record PlayAnimPacket(int entityId, AnimSpec spec) {
    public static void encode(PlayAnimPacket msg, FriendlyByteBuf buf) {
        buf.writeVarInt(msg.entityId);
        msg.spec.write(buf);
    }

    public static PlayAnimPacket decode(FriendlyByteBuf buf) {
        return new PlayAnimPacket(buf.readVarInt(), AnimSpec.read(buf));
    }

    public static void handle(PlayAnimPacket msg, Supplier<NetworkEvent.Context> ctx) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.csm.hybrids.client.ClientPacketHandler.handleAnim(msg.entityId, msg.spec));
        ctx.get().setPacketHandled(true);
    }
}
