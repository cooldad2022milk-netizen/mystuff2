package com.csm.hybrids.loot;

import com.google.common.base.Suppliers;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import it.unimi.dsi.fastutil.objects.ObjectArrayList;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;
import net.minecraftforge.common.loot.IGlobalLootModifier;
import net.minecraftforge.common.loot.LootModifier;
import net.minecraftforge.registries.ForgeRegistries;
import org.jetbrains.annotations.NotNull;

import java.util.List;
import java.util.function.Supplier;

/**
 * Rarely slips a devil heart into structure chests (until devils that drop their hearts exist).
 */
public class DevilHeartLootModifier extends LootModifier {
    public static final Supplier<Codec<DevilHeartLootModifier>> CODEC = Suppliers.memoize(() ->
            RecordCodecBuilder.create(inst -> codecStart(inst)
                    .and(ForgeRegistries.ITEMS.getCodec().fieldOf("item").forGetter(m -> m.item))
                    .and(ResourceLocation.CODEC.listOf().fieldOf("tables").forGetter(m -> m.tables))
                    .and(Codec.FLOAT.fieldOf("chance").forGetter(m -> m.chance))
                    .apply(inst, DevilHeartLootModifier::new)));

    private final Item item;
    private final List<ResourceLocation> tables;
    private final float chance;

    public DevilHeartLootModifier(LootItemCondition[] conditions, Item item, List<ResourceLocation> tables, float chance) {
        super(conditions);
        this.item = item;
        this.tables = tables;
        this.chance = chance;
    }

    @Override
    protected @NotNull ObjectArrayList<ItemStack> doApply(ObjectArrayList<ItemStack> loot, LootContext context) {
        if (tables.contains(context.getQueriedLootTableId()) && context.getRandom().nextFloat() < chance) {
            loot.add(new ItemStack(item));
        }
        return loot;
    }

    @Override
    public Codec<? extends IGlobalLootModifier> codec() {
        return CODEC.get();
    }
}
