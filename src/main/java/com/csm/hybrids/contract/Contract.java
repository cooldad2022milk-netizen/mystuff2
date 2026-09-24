package com.csm.hybrids.contract;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * A contract with a devil, as Public Safety's hunters make them. A contractor stays human (or whatever they already
 * are) and borrows a part of the devil, paying its price:
 * <ul>
 *   <li>FOX_HEAD - the Fox Devil only lends its <b>head</b> to hunters it finds handsome (Aki, the Vice Captain):
 *       make the fox sign, say "Kon!" and its jaws close on the target. The fox eats a little of you each time.</li>
 *   <li>FOX_PAW - everyone else the Fox Devil deals with only gets a <b>paw</b> (Nomo, Nakamura): it comes down on
 *       the target from above, or sweeps in front of you. A separate contract with the same devil.</li>
 *   <li>CURSE - stab the same thing three times with the nail and the Curse Devil appears behind it, seizes it by
 *       the arms and bites. Every time it comes, it takes some of your lifespan.</li>
 *   <li>FUTURE - the Future Devil lives in your right eye and shows you a few seconds ahead.</li>
 *   <li>GHOST - paid for with your right eye (Himeno): the Ghost Devil's invisible right arm does what yours does.</li>
 *   <li>SNAKE - Sawatari's: a fingernail per command. The Snake Devil (green, a red eye in black, a mouth of
 *       interlocking hands) swallows things whole and later spits them back out, healed, to fight for you; or
 *       swats with its tail.</li>
 *   <li>OCTOPUS - Yoshida's (the price is between him and the devil): cross two fingers and its tentacles come out of
 *       clouds of ink to seize, lift and smash; or it sprays ink.</li>
 *   <li>DOLL - Santa Claus's: whoever you touch becomes your doll, and every doll that touches someone makes another.
 *       It does nothing to devils, hybrids or fiends, and a doll you leave behind falls over, lifeless.</li>
 * </ul>
 * The mobs of the Fox, Curse, Future and Ghost devils still exist, but nobody becomes them any more: their loot is a
 * contract, not an essence. The Snake, Octopus and Doll devils are never met: only their contracts turn up.
 */
public enum Contract {
    FOX_HEAD("fox_head", HybridType.FOX, 0xF4F0E6),
    FOX_PAW("fox_paw", HybridType.FOX, 0xE8D2B4),
    CURSE("curse", HybridType.CURSE, 0xD8D0B8),
    FUTURE("future", HybridType.FUTURE, 0xC8A870),
    GHOST("ghost", HybridType.GHOST, 0xE8E0F0),
    SNAKE("snake", HybridType.NONE, 0x5A9A3A),
    OCTOPUS("octopus", HybridType.NONE, 0x9A4A7A),
    DOLL("doll", HybridType.NONE, 0xE8C8B8);

    public final String id;
    /** The devil the contract is with (NONE for the devils that only exist as contracts in this world). */
    public final HybridType devil;
    public final int color;

    Contract(String id, HybridType devil, int color) {
        this.id = id;
        this.devil = devil;
        this.color = color;
    }

    public int bit() {
        return 1 << ordinal();
    }

    /** The moves this contract adds to the ability wheel. */
    public List<Ability> abilities() {
        return ContractAbilities.forContract(this);
    }

    public Component displayName() {
        return Component.translatable("contract.csm." + id);
    }

    /** Registry name of the contract item. */
    public String itemName() {
        return switch (this) {
            case FOX_HEAD -> "fox_devil_contract_head";
            case FOX_PAW -> "fox_devil_contract_paw";
            default -> id + "_devil_contract";
        };
    }

    public static Contract byId(String id) {
        String s = id.toLowerCase(Locale.ROOT);
        for (Contract c : values()) {
            if (c.id.equals(s)) {
                return c;
            }
        }
        return null;
    }

    /** The contracts held in a {@link com.csm.hybrids.hybrid.HybridData} bit mask, in wheel order. */
    public static List<Contract> fromMask(int mask) {
        List<Contract> out = new ArrayList<>();
        for (Contract c : values()) {
            if ((mask & c.bit()) != 0) {
                out.add(c);
            }
        }
        return out;
    }
}
