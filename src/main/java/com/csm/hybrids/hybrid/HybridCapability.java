package com.csm.hybrids.hybrid;

import com.csm.hybrids.CsmMod;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.CapabilityManager;
import net.minecraftforge.common.capabilities.CapabilityToken;
import net.minecraftforge.common.capabilities.ICapabilitySerializable;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.common.util.LazyOptional;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public final class HybridCapability {
    public static final Capability<HybridData> CAP = CapabilityManager.get(new CapabilityToken<>() {
    });
    public static final ResourceLocation KEY = CsmMod.id("hybrid");

    public static void register(RegisterCapabilitiesEvent event) {
        event.register(HybridData.class);
    }

    @Nullable
    public static HybridData get(@Nullable Entity entity) {
        if (entity == null) {
            return null;
        }
        return entity.getCapability(CAP).orElse(null);
    }

    public static final class Provider implements ICapabilitySerializable<CompoundTag> {
        private final HybridData data = new HybridData();
        private final LazyOptional<HybridData> optional = LazyOptional.of(() -> data);

        @Override
        public <T> @NotNull LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
            return cap == CAP ? optional.cast() : LazyOptional.empty();
        }

        @Override
        public CompoundTag serializeNBT() {
            return data.save();
        }

        @Override
        public void deserializeNBT(CompoundTag nbt) {
            data.load(nbt);
        }

        public void invalidate() {
            optional.invalidate();
        }
    }

    private HybridCapability() {
    }
}
