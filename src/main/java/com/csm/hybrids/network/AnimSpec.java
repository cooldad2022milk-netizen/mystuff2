package com.csm.hybrids.network;

import net.minecraft.network.FriendlyByteBuf;

/**
 * Everything a client needs to play one hybrid action on a player:
 * a PlayerAnimator body animation plus a GeckoLib animation on the devil parts.
 *
 * @param playerAnim PlayerAnimator animation id (path inside the csm namespace), "" for none
 * @param controller GeckoLib controller that plays {@code geoAnim}
 * @param geoAnim    GeckoLib triggerable animation, "" for none
 * @param fx         bone effect group made visible while running (e.g. "flame" shows fx_flame_* bones)
 * @param revs       chainsaw only: run the chains at full rev while active
 * @param kind       {@link #ABILITY}, {@link #TRANSFORM}, {@link #REVERT}, {@link #HEART} or {@link #STOP}
 * @param duration   ticks
 */
public record AnimSpec(String playerAnim, String controller, String geoAnim, String fx, boolean revs, int kind,
                       int duration) {
    public static final int ABILITY = 0;
    public static final int TRANSFORM = 1;
    public static final int REVERT = 2;
    public static final int HEART = 3;
    public static final int STOP = 4;

    public static AnimSpec stop() {
        return new AnimSpec("", "", "", "", false, STOP, 0);
    }

    public void write(FriendlyByteBuf buf) {
        buf.writeUtf(playerAnim);
        buf.writeUtf(controller);
        buf.writeUtf(geoAnim);
        buf.writeUtf(fx);
        buf.writeBoolean(revs);
        buf.writeByte(kind);
        buf.writeVarInt(duration);
    }

    public static AnimSpec read(FriendlyByteBuf buf) {
        return new AnimSpec(buf.readUtf(), buf.readUtf(), buf.readUtf(), buf.readUtf(), buf.readBoolean(),
                buf.readByte(), buf.readVarInt());
    }
}
