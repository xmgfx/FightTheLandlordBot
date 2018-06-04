#!/usr/bin/python
# -*- coding: UTF-8 -*-

import simulator
import json
import random
import numpy as np
#from PolicyNetwork import PlayModel

# Fight The Landlord executor

# Initialization using the JSON input
class FTLBot:
    def __init__(self, playmodel, exnetwork,data, dataType = "Judge"):
        self.dataType = dataType
        self.playmodel = playmodel
        self.exnetwork=exnetwork
        if dataType == "JSON": # JSON req
            rawInput = json.loads(data)
            rawRequest = rawInput["requests"]
            initInfo = rawRequest[0]
            initHistory = initInfo["history"]
            myBotID = 2 if len(initHistory[0]) else 1 if len(initHistory[1]) else 0
            myCards = initInfo["own"]
            myCards.sort()
            publicCard = initInfo["publiccard"]
            nowTurn = len(rawInput["responses"])

            # Construct game simulator
            sim = simulator.FTLSimulator(myBotID, nowTurn, publicCard)
            sim.deal(myCards)

            # Retrace the history plays
            # first request
            if myBotID == 1:
                sim.play(0, initHistory[1])
            if myBotID == 2:
                sim.play(0, initHistory[0])
                sim.play(1, initHistory[1])
            # following rounds
            roundN = len(rawInput["responses"])
            for rnd in range(roundN):
                otherPlayerHistory = rawRequest[rnd+1]["history"]
                plays = [rawInput["responses"][rnd], otherPlayerHistory[0], otherPlayerHistory[1]]
                for turn in range(3):
                    #print(str((myBotID+turn)%3)+" Plays "+simulator.Hand(plays[turn]).report())
                    sim.play((myBotID+turn)%3, plays[turn])

            # check if this is my turn
            lastHistory = rawRequest[roundN]["history"]
            sim.setCardsToFollow(lastHistory[1] or lastHistory[0])
            self.simulator = sim

        elif dataType == "Judge": # data from judgement
            sim = simulator.FTLSimulator(data["ID"], data["nowTurn"], data["publicCard"])
            sim.deal(data["deal"])
            sim.setHistory(data["history"])
            self.simulator = sim

    def makeData(self, data):
        if self.dataType == "JSON":
            return json.dumps({"response": data})
        elif self.dataType == "Judge":
            return data

    # Return the decision based on type
    def makeDecision(self):
        lastHand = simulator.Hand(self.simulator.cardsToFollow)   
        possiblePlays = simulator.CardInterpreter.splitCard(self.simulator.myCards, lastHand)
        #print(possiblePlays)
        kickerNum = lastHand.kickerNum

        # @TODO You need to modify the following part !!
        # A little messed up ...
        if not len(possiblePlays):
            return self.makeData([])
        
        sim = self.simulator
        net_input = self.playmodel.ch2input(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay)
        one_hot_t = self.playmodel.hand2one_hot(possiblePlays)
        choice1 = self.playmodel.getActions(net_input,sim.nowPlayer,one_hot_t)
        index=np.argmax(one_hot_t)
        cardstoplay=np.zeros(15)
        if index>=42 and index<=67:
            cardstoplay[choice1[0]]=3
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice2 = self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t) 
        elif index>=68 and index<=93:
            cardstoplay[choice1[0]]=4
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice2 = self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t) 
            if len(choice2)==1:
                sim.myCards[choice2[0]]=sim.myCards[choice2[0]]-1
            if len(choice2)==2:   
                sim.myCards[choice2[0]]=sim.myCards[choice2[0]]-2
            sim.myCards1=sim.myCards
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards1,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice3 = self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t) 
            choice2=choice2.append(choice3)    
        elif index>=241 and index<=285:
            cardstoplay[choice1[0]]=3
            cardstoplay[choice1[3]]=3 
            if index>=252:
                cardstoplay[choice1[6]]=3
                if index>=262:
                    cardstoplay[choice1[9]]=3
                    if index>=271:
                        cardstoplay[choice1[12]]=3
                        if index>=278:
                            cardstoplay[choice1[15]]=3
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice2 = self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t)   
            for i in range(cardstoplay.count(3)-1):  
                sim.myCards[choice2[0]]=sim.myCards[choice2[0]]-1
                extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
                extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
                choice3= self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t) 
                choice2=choice2.append(choice3) 
                #sim.myCards=sim.myCards1
                i=i+1
        elif index>=286 and index<=330:
            cardstoplay[choice1[0]]=3
            cardstoplay[choice1[3]]=3
            if index>=296:
                cardstoplay[choice1[6]]=3                
                if index>=306:
                    cardstoplay[choice1[9]]=3                    
                    if index>=315:
                        cardstoplay[choice1[12]]=3                                                  
                        if index>=323:
                            cardstoplay[choice1[15]]=3  
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice2 = self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t)   
            for i in range(cardstoplay.count(3)-1):  
                sim.myCards[choice2[0]]=sim.myCards[choice2[0]]-2
                extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
                extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
                choice3= self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t) 
                choice2=choice2.append(choice3) 
                #sim.myCards=sim.myCards1
                i=i+1                                        
        elif index>=342 and index<=351:
            cardstoplay[choice1[0]]=4
            cardstoplay[choice1[3]]=4
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice2 = self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t)   
            sim.myCards[choice2[0]]=sim.myCards[choice2[0]]-1
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice3= self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t) 
            choice2=choice2.append(choice3) 
                                           
        elif index>=352 and index<=363:
            cardstoplay[choice1[0]]=4
            cardstoplay[choice1[3]]=4
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice2 = self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t)        
            sim.myCards[choice2[0]]=sim.myCards[choice2[0]]-2
            extra_net_input=self.exnetwork.extra_chinput(sim.nowPlayer,sim.myCards,sim.publicCard,sim.history,sim.lastPlay,sim.lastLastPlay,sim.cardstoplay)
            extra_one_hot_t = self.exnetwork.hand2one_hot(possiblePlays)
            choice3= self.playmodel.getActions(extra_net_input,sim.nowPlayer,extra_one_hot_t) 
            choice2=choice2.append(choice3) 
            
            
        
       
        if (index>=42 and index<=93) or (index>=196 and index<=363):
            choice=choice1.append(choice2)
        else:           
            choice=choice1


        # Add kickers, if first element is dict, the choice must has some kickers
        # @TODO get kickers from kickers model
        if choice and isinstance(choice[0],dict):
            tmphand = choice[1:]
            lenh = len(tmphand)
            allkickers = simulator.CardInterpreter.getKickers(sim.myCards, choice[0]["kickerNum"], list(set(tmphand)))
            kickers = []
            if choice[0]["type"] == "Trio":
                kickers = random.sample(allkickers, choice[0]["chain"])
            elif choice[0]["type"] == "Four":
                kickers = random.sample(allkickers, choice[0]["chain"]*2)
            for k in kickers:
                tmphand.extend(k)
            choice = tmphand
        cardChoice = simulator.CardInterpreter.selectCardByHand(self.simulator.myCards, choice)


        # You need to modify the previous part !!
        return self.makeData(cardChoice)