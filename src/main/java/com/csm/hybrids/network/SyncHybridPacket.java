package com.csm.hybrids.network;

import com.csm.hybrids.hybrid.HybridData;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Server -> client copy of a player's hybrid state. {@code state.full} is only set for the owner. */
public record SyncHybridPacket(int entityId, HybridData.SyncState state) {
    public static SyncHybridPacket of(int entityId, HybridData data, boolean full) {
        FriendlyByteBuf tmp = new FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        data.writeSync(tmp, full);
        HybridData.SyncState s = new HybridData.SyncState();
        HybridData.readSyncInto(tmp, s);
        tmp.release();
        return new SyncHybridPacket(entityId, s);
    }

    public static void encode(SyncHybridPacket msg, FriendlyByteBuf buf) {
        buf.writeVarInt(msg.entityId);
        HybridData.SyncState s = msg.state;
        buf.writeByte(s.type.ordinal());
        buf.writeBoolean(s.transformed);
        buf.writeFloat(s.blood);
        buf.writeByte(s.selected);
        buf.writeVarInt(s.contracts);
        buf.writeBoolean(s.full);
        if (s.full) {
            for (int i = 0; i < HybridData.MAX_ABILITIES; i++) {
                buf.writeVarInt(s.cooldowns[i]);
                buf.writeVarInt(s.cooldownMax[i]);
            }
        }
    }

    public static SyncHybridPacket decode(FriendlyByteBuf buf) {
        int id = buf.readVarInt();
        HybridData.SyncState s = new HybridData.SyncState();
        HybridData.readSyncInto(buf, s);
        return new SyncHybridPacket(id, s);
    }

    public static void handle(SyncHybridPacket msg, Supplier<NetworkEvent.Context> ctx) {
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.csm.hybrids.client.ClientPacketHandler.handleSync(msg.entityId, msg.state));
        ctx.get().setPacketHandled(true);
    }
}
