package com.csm.hybrids.hybrid;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.contract.Contract;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.List;

/**
 * Per-player hybrid state (Forge capability). Saved with the player and synced to clients.
 * <p>
 * Besides the devil living in them ({@link #type()}), a player can hold devil <b>contracts</b>; their moves follow the
 * type's own moves on the ability wheel ({@link #abilities()}), so a plain human with a contract has a wheel too.
 */
public class HybridData {
    /** A hybrid's own moves plus every contract's fit (the wheel shrinks its icons past 16). */
    public static final int MAX_ABILITIES = 24;
    public static final float MAX_BLOOD = 100f;

    private HybridType type = HybridType.NONE;
    private boolean transformed;
    private float blood;
    private int selected;
    private final int[] cooldowns = new int[MAX_ABILITIES];
    private final int[] cooldownMax = new int[MAX_ABILITIES];
    /** Bit mask of {@link Contract#bit()}. */
    private int contracts;
    /** Hearts of lifespan the Curse Devil has taken so far. */
    private int curseToll;
    /** The wheel: the type's moves then each contract's. Rebuilt when the type or the contracts change. */
    private List<Ability> abilities;
    /**
     * While a hybrid is taken over by its devil (Pochita's true form out of Denji), the hybrid it really is; NONE
     * otherwise. Only the real type is ever saved: logging out mid-takeover wakes you up as yourself.
     */
    private HybridType baseType = HybridType.NONE;
    /** Server: ticks of the takeover left. */
    public int takeoverTicks;

    /** Server: the ability currently being performed (trigger animations included). */
    public AbilityRun activeRun;
    /** Server: blood value last sent to the client (only resync when it changes noticeably). */
    public float lastSyncedBlood = -1;
    private boolean dirty;

    /** Client: render/animation state. Typed as Object so this class stays safe on dedicated servers. */
    public Object clientState;

    public HybridType type() {
        return type;
    }

    public boolean isHybrid() {
        return type != HybridType.NONE;
    }

    /** Whether there is anything on the ability wheel (a hybrid, a devil, or a human contractor). */
    public boolean hasAbilities() {
        return !abilities().isEmpty();
    }

    /** Everything on the ability wheel, in order: the type's moves, then the moves of each contract held. */
    public List<Ability> abilities() {
        if (abilities == null) {
            List<Ability> list = new ArrayList<>(type.abilities());
            for (Contract c : Contract.fromMask(contracts)) {
                list.addAll(c.abilities());
            }
            abilities = List.copyOf(list.subList(0, Math.min(list.size(), MAX_ABILITIES)));
        }
        return abilities;
    }

    /** The hybrid this player really is (their type, or the hybrid under a takeover form). */
    public HybridType baseType() {
        return baseType != HybridType.NONE ? baseType : type;
    }

    /** Whether the devil has taken this hybrid over (the type is a {@link HybridType#takeover()} form). */
    public boolean inTakeover() {
        return baseType != HybridType.NONE;
    }

    /** The devil takes over: the wheel and the body become the takeover form's until {@link #endTakeover()}. */
    public void startTakeover(HybridType form, int ticks) {
        baseType = baseType();
        type = form;
        transformed = true;
        takeoverTicks = ticks;
        abilities = null;
        selected = 0;
        clearCooldowns();
        markDirty();
    }

    /** The devil lets go: back to the real hybrid, in human form. */
    public void endTakeover() {
        if (baseType == HybridType.NONE) {
            return;
        }
        type = baseType;
        baseType = HybridType.NONE;
        takeoverTicks = 0;
        transformed = false;
        abilities = null;
        selected = 0;
        clearCooldowns();
        markDirty();
    }

    public void setType(HybridType type) {
        baseType = HybridType.NONE;
        takeoverTicks = 0;
        if (this.type != type) {
            this.type = type;
            this.abilities = null;
            this.selected = 0;
            this.transformed = false;
            clearCooldowns();
            markDirty();
        }
    }

    // ------------------------------------------------------------------ contracts
    public boolean hasContract(Contract c) {
        return (contracts & c.bit()) != 0;
    }

    public boolean hasContracts() {
        return contracts != 0;
    }

    public int contractMask() {
        return contracts;
    }

    public List<Contract> contracts() {
        return Contract.fromMask(contracts);
    }

    /** @return false if the contract was already held. */
    public boolean addContract(Contract c) {
        if (hasContract(c)) {
            return false;
        }
        setContractMask(contracts | c.bit());
        return true;
    }

    /** @return false if the contract was not held. */
    public boolean removeContract(Contract c) {
        if (!hasContract(c)) {
            return false;
        }
        setContractMask(contracts & ~c.bit());
        return true;
    }

    public void setContractMask(int mask) {
        if (mask != contracts) {
            // contract moves sit after the type's: dropping one shifts the slots behind it
            boolean removed = (contracts & ~mask) != 0;
            contracts = mask;
            abilities = null;
            if (removed) {
                clearCooldowns();
            }
            selected = Mth.clamp(selected, 0, Math.max(0, abilities().size() - 1));
            markDirty();
        }
    }

    public int curseToll() {
        return curseToll;
    }

    public void setCurseToll(int hearts) {
        curseToll = Math.max(0, hearts);
        markDirty();
    }

    public boolean isTransformed() {
        return transformed;
    }

    public void setTransformed(boolean transformed) {
        if (this.transformed != transformed) {
            this.transformed = transformed;
            markDirty();
        }
    }

    public float blood() {
        return blood;
    }

    public void setBlood(float blood) {
        this.blood = Mth.clamp(blood, 0, MAX_BLOOD);
    }

    public void addBlood(float amount) {
        setBlood(blood + amount);
    }

    public int selected() {
        return selected;
    }

    public void setSelected(int selected) {
        int count = abilities().size();
        int s = count == 0 ? 0 : Mth.clamp(selected, 0, count - 1);
        if (s != this.selected) {
            this.selected = s;
            markDirty();
        }
    }

    public int cooldown(int index) {
        return index >= 0 && index < MAX_ABILITIES ? cooldowns[index] : 0;
    }

    public int cooldownMax(int index) {
        return index >= 0 && index < MAX_ABILITIES ? cooldownMax[index] : 0;
    }

    public void setCooldown(int index, int ticks) {
        if (index >= 0 && index < MAX_ABILITIES) {
            cooldowns[index] = ticks;
            cooldownMax[index] = Math.max(ticks, 1);
            markDirty();
        }
    }

    public void clearCooldowns() {
        for (int i = 0; i < MAX_ABILITIES; i++) {
            cooldowns[i] = 0;
            cooldownMax[i] = 0;
        }
    }

    /** Counts cooldowns down by one tick (both sides, client just for the HUD). */
    public void tickCooldowns() {
        for (int i = 0; i < MAX_ABILITIES; i++) {
            if (cooldowns[i] > 0) {
                cooldowns[i]--;
            }
        }
    }

    public void markDirty() {
        dirty = true;
    }

    public boolean consumeDirty() {
        boolean d = dirty;
        dirty = false;
        return d;
    }

    // ------------------------------------------------------------------ persistence
    public CompoundTag save() {
        CompoundTag tag = new CompoundTag();
        tag.putString("type", baseType().id);
        tag.putBoolean("transformed", transformed && !inTakeover());
        tag.putFloat("blood", blood);
        tag.putInt("selected", selected);
        tag.putIntArray("cooldowns", cooldowns.clone());
        tag.putInt("contracts", contracts);
        tag.putInt("curse_toll", curseToll);
        return tag;
    }

    public void load(CompoundTag tag) {
        type = HybridType.byId(tag.getString("type"));
        baseType = HybridType.NONE;
        takeoverTicks = 0;
        if (!type.playable()) {
            type = type.takeover() ? type.host() : HybridType.NONE; // (contract devils: saved before they were contracts)
        }
        contracts = tag.getInt("contracts");
        curseToll = tag.getInt("curse_toll");
        abilities = null;
        transformed = tag.getBoolean("transformed") && type != HybridType.NONE;
        blood = tag.getFloat("blood");
        selected = tag.getInt("selected");
        int[] cd = tag.getIntArray("cooldowns");
        for (int i = 0; i < MAX_ABILITIES; i++) {
            cooldowns[i] = i < cd.length ? cd[i] : 0;
            cooldownMax[i] = Math.max(cooldowns[i], 1);
        }
    }

    /** Copy on respawn / dimension travel. Dying knocks you back into human form. */
    public void copyFrom(HybridData other, boolean death) {
        load(other.save());
        if (death) {
            transformed = false;
            clearCooldowns();
        }
        markDirty();
    }

    // ------------------------------------------------------------------ network
    public void writeSync(FriendlyByteBuf buf, boolean full) {
        buf.writeByte(type.ordinal());
        buf.writeBoolean(transformed);
        buf.writeFloat(blood);
        buf.writeByte(selected);
        buf.writeVarInt(contracts);
        buf.writeBoolean(full);
        if (full) {
            for (int i = 0; i < MAX_ABILITIES; i++) {
                buf.writeVarInt(cooldowns[i]);
                buf.writeVarInt(cooldownMax[i]);
            }
        }
    }

    /** Applies a sync payload written by {@link #writeSync}. */
    public static void readSyncInto(FriendlyByteBuf buf, SyncState out) {
        out.type = HybridType.byOrdinal(buf.readByte());
        out.transformed = buf.readBoolean();
        out.blood = buf.readFloat();
        out.selected = buf.readByte();
        out.contracts = buf.readVarInt();
        out.full = buf.readBoolean();
        if (out.full) {
            for (int i = 0; i < MAX_ABILITIES; i++) {
                out.cooldowns[i] = buf.readVarInt();
                out.cooldownMax[i] = buf.readVarInt();
            }
        }
    }

    public void applySync(SyncState s) {
        if (this.type != s.type || this.contracts != s.contracts) {
            this.abilities = null;
        }
        this.type = s.type;
        this.contracts = s.contracts;
        this.transformed = s.transformed;
        this.blood = s.blood;
        this.selected = s.selected;
        if (s.full) {
            System.arraycopy(s.cooldowns, 0, cooldowns, 0, MAX_ABILITIES);
            System.arraycopy(s.cooldownMax, 0, cooldownMax, 0, MAX_ABILITIES);
        }
    }

    public static final class SyncState {
        public HybridType type = HybridType.NONE;
        public boolean transformed;
        public float blood;
        public int selected;
        public int contracts;
        public boolean full;
        public final int[] cooldowns = new int[MAX_ABILITIES];
        public final int[] cooldownMax = new int[MAX_ABILITIES];
    }
}
