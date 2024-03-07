# -*- coding: utf-8 -*-

# Contributors:
#    Paco Mora Caselles <pacomoracaselles@gmail.com>

"""This file contains the implementation of the CBSD algorithm.
"""

from subgroups.algorithms.subgroup_sets.bsd import BSD
from subgroups.core.pattern import Pattern
from subgroups.data_structures.bitset_bsd import BitsetDictionary
from bitarray import bitarray

class CPBSD(BSD):

    __slots__ = ()

    def _handle_individual_result(self, individual_result: tuple) -> tuple[BitsetDictionary, BitsetDictionary, list]:
        """Private method to handle each individual result generated by the algorithm.

        :param individual_result: The individual result generated by the algorithm. It consists of a tuple with the values (selCond, sCurr, oe, quality,CcondPos,CcondNeg, cCurrPos, cCurrNeg,newSelRel,tp,fp).
        """
        self._visited_subgroups += 1
        selCond = individual_result[0]
        sCurr = individual_result[1]
        oe = individual_result[2]
        quality = individual_result[3]
        CcondPos = individual_result[4]
        CcondNeg = individual_result[5]
        cCurrPos = individual_result[6]
        cCurrNeg = individual_result[7]
        newSelRel = individual_result[8]
        tp = individual_result[9]
        fp = individual_result[10]
        # if optimistic estimate > min or k-subgroups is not full
        if(oe >= self._k_subgroups[0][0] or len(self._k_subgroups) < self.num_subgroups):
            # Add the current selector to the list of new selectors added to the conditional pattern
            newSelRel.append((oe, sCurr))
            # Add the current selector with the pattern to the dictionaries of positive and negative entries
            CcondPos,CcondNeg = self._attach(cCurrPos, cCurrNeg, CcondPos, CcondNeg, sCurr, selCond)
            #if quality > min or k-subgroups is not full
            if quality >= self._k_subgroups[0][0] or len(self._k_subgroups) < self.num_subgroups:
                # sg = conditional pattern + current selector
                if selCond:
                    sg = selCond.copy()
                    sg.add_selector(sCurr)
                else:
                    sg = Pattern([sCurr])
                r= self._checkRel(self._k_subgroups, cCurrPos,quality,sg)
                # If the subgroup is relevant, we add it to the list of k-subgroups
                if r:
                                        # (quality, subgroup, bits, optimistic_estimate,(tp,fp))
                    self._k_subgroups.append((quality, sg, cCurrPos + cCurrNeg,oe,(tp,fp)))
                    self._k_subgroups = sorted(self._k_subgroups, reverse=False, key=lambda x: x[0])
                    # Check if the subgroups in k_subgroups are still relevant
                    self._checkRelevancies(cCurrPos, sg,quality)
                    # If k_subgroups is full, remove the subgroup with the lowest quality
                    if len(self._k_subgroups) > self.num_subgroups:
                        # Remove lowest quality subgroup
                        self._k_subgroups.pop(0)
                        self._unselected_subgroups += 1
                else:
                    self._unselected_subgroups += 1
            else:
                self._unselected_subgroups += 1
        else:
            self._unselected_subgroups +=1
        return CcondPos,CcondNeg,newSelRel

    def _checkRelevancies(self,ccurrPos : bitarray,sg : Pattern,quality : float) -> None:
        """Internal method to check relevacies in _k_subgroups.

        :param ccurrPos: bitarray of positive and negative instances
        :param sg: Pattern that represents a subgroup
        :param quality: sg quality
        """
        if type(quality) is not float:
            raise TypeError("Parameter 'quality' must be a float.")
        if type(ccurrPos) is not bitarray:
            raise TypeError("Parameter 'ccurrPos' must be a bitarray.")
        if type(sg) is not Pattern:
            raise TypeError("Parameter 'sg' must be a Pattern.")
        # Eliminate the dummy subgroup
        if len(self._k_subgroups[0][1]) == 0:
            self._k_subgroups.pop(0)
        # New list of k_subgroups
        aux =[]
        for tuple in self._k_subgroups:
            i = 0
            rel = False
            # If the subgroup in the list is the one we are checking in this call or they have different quality --> is relevant
            if tuple[1] == sg or tuple[0] != quality:
                rel = True
            while i < len(ccurrPos) and not rel:
                # If the new subgroup does not contain the positve instances of the old subgroup --> is relevant
                if tuple[2][i] and not ccurrPos[i]:
                    rel = True
                i = i + 1
            # We add the old subgroup to the new list of k_subgroups if it is relevant
            if rel:
                aux.append(tuple)
            else:
                self._irrelevants.append((tuple[1], tuple[0], tuple[2]))
                self._unselected_subgroups += 1
        self._k_subgroups = aux

    def _checkRel(self, res: list, ccurrPos: bitarray, quality: float, sCurr: Pattern) -> bool:
        """Internal method to check if sCurr is relevant in res.

        :param res: list of tuples
        :param ccurrPos: bitarray of positive instances
        :param quality: sCurr quality
        :param sCurr: Pattern of the subgroup found
        :return: check if ccurrPos + ccurrNeg is relevant in res
        """
        if type(res) is not list:
            raise TypeError("Parameter 'res' must be a list.")
        if type(ccurrPos) is not bitarray:
            raise TypeError("Parameter 'ccurrPos' must be a bitarray.")
        if type(quality) is not float:
            raise TypeError("Parameter 'quality' must be a float.")
        if type(sCurr) is not Pattern:
            raise TypeError("Parameter 'sCurr' must be a Pattern.")
        #if is empty
        if not res[0][1]:
            return True
        for tuple in res:
            # If the quality is not the same --> is relevant
            if(tuple[0] == quality):
                i = 0
                rel = False
                while i < len(ccurrPos):
                    # If the old subgroup does not contain the positive instances of the new subgroup --> is relevant
                    if not tuple[2][i] and ccurrPos[i]:
                        rel = True
                        break
                    i = i +1
                if not rel:
                    # If the subgroups are the same in positive instances or the new subgroup contains the old subgroup in positive instances, we prune the shorter subgroup
                    if len(tuple[1]) > len(sCurr):
                        self._irrelevants.append((sCurr, quality, ccurrPos))
                        return False
                    else:
                        self._k_subgroups.remove(tuple)
                        self._irrelevants.append((tuple[1], tuple[0], tuple[2]))
                        self._unselected_subgroups += 1
                        return True
        return True