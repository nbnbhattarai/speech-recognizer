from nltk import sent_tokenize
import tokenizer
import pickle
import operator
# import dictionary
# import word2vec


class nGram:
    """
    This is a class which represent n-gram and helps to
    calculate probability too.
    """

    def __init__(self, filename=None, N=4):
        """
        filename : open nGram data from file.
        N : value of n in nGram, it's default value
        is 4, so it's four gram and stores bigram, trigram and 4 gram.
        """
        self.filename = filename
        self.N = N
        self.words = []
        self.gram = [{} for i in range(0, N)]

    def get_grams(self, tokens, n):
        # word_vec_er = word2vec.WordVectorRep(dict=self.dict)
        # tokens_vec = tokens
        tokens_vec = []
        for t in tokens:
            tokens_vec.append(self.words.index(t))
        return [tuple(tokens_vec[i:i + n]) for i in
                range(0, len(tokens_vec) - n + 1)]

    def add_tokens(self, tokens):
        """
        Update nGram data with given token list.
        """
        for t in tokens:
            if t not in self.words:
                self.words.append(t)

        for i in range(1, self.N + 1):
            ngram_tup = self.gram[i - 1].keys()
            n_gram = self.get_grams(tokens, i)
            # print(n_gram)
            for g in n_gram:
                if g in ngram_tup:
                    self.gram[i - 1][g] += 1  # increase count by one
                else:
                    self.gram[i - 1][g] = 1  # if first entry then count is 1

    def write(self, filename):
        """
        We are going to use pickle to write data object to file.
        """
        print("Writing file.")
        try:
            file = open(filename, 'wb')
            file.write(pickle.dumps(self.__dict__))
            print("[ done ]")
        except FileNotFoundError:
            print("[ error ]")

    def open_from_file(self, filename):
        print("Opening NGram database from file " + filename + ' ', end='')
        try:
            file = open(filename, 'rb')
            datapickle = file.read()
            file.close()
            self.__dict__ = pickle.loads(datapickle)
            print("[ done ]")
        except FileNotFoundError:
            print("[ error ]")

    def trainFromFile(self, filename):
        self.filename = filename
        print("Training NGram from file " + filename, end=' .')
        try:
            file = open(filename, 'r', encoding='ascii',
                        errors='surrogateescape')
            text_data = file.read().lower()
            # let's replace newline char with white space
            text_data = text_data.replace('\n', ' ')
            # let's tokenize sentences from text_data.
            # I use sent_tokenize nltk function to tokenize the sentences.
            sents = sent_tokenize(text_data)
            # print('sent:', sents)
            # let's iterate over sentences and tokenize words and update
            # n-gram data
            tok = tokenizer.Tokenizer()
            for s in sents:
                # tokens = nltk.word_tokenize(s)
                tokens = tok.word_tokenize(s)
                # print(tokens, 'added!')
                self.add_tokens(tokens)
            print(' [ done ]')
        except FileNotFoundError:
            print(' [ error ]')

    def get_nw_ngram(self, pw, n):
        """
        It returns list of next words having high probabilities by
        using last (n-1) words of pw(previous words) using n gram.
        """
        next_words = []
        # if pw(previous words) count is lesser than n-1 then we
        # cannot use ngram(markov model) to find next word.
        if len(pw) < n - 1:
            return []
        # add these count to the next word's probability
        # increase probability if next word is found by higher grams.
        pro_dist = [0, 100, 200]

        previous_words = pw[-n + 1:]
        # print('previous words:', [self.words[x] for x in previous_words])
        for (wt, c) in self.gram[n - 1].items():
            words_list = list(wt)
            if previous_words == words_list[:-1]:
                # save next word with probability as tuple
                n_w = words_list[-1]
                # if n_w in self.gram[0].keys():
                # probab = float(c) / float(self.gram[0][(n_w,)])
                probab = c + pro_dist[n - 2]
                # print('type prob:', type(probab))
                # print('probab : ', probab)
                next_words.append((n_w, probab))
        next_words = list(set(next_words))
        next_words = sorted(next_words, key=operator.itemgetter(1),
                            reverse=True)
        return next_words[:]   # return list of (word,prob) tuple

    def prob(self, word_list):
        """
        It returns unique next word from word_list list of tuples
        it adds probability if words are appearing more than once.
        """
        words = list(set([w[0] for w in word_list]))
        words_with_probs = []
        for w in words:
            prob = 0
            for wl in word_list:
                if w == wl[0]:
                    prob += wl[1]
            words_with_probs.append((w, prob))
        return words_with_probs

    def get_next_word(self, till):
        # get list of tupels (word_id, count)
        from_bigram = self.get_nw_ngram(till, 2)
        from_trigram = self.get_nw_ngram(till, 3)
        from_fourgram = self.get_nw_ngram(till, 4)

        word_list = from_bigram + from_trigram + from_fourgram
        word_list = self.prob(word_list)
        word_list = sorted(word_list, key=operator.itemgetter(1),
                           reverse=True)
        return word_list[:]

    def get_count(self, sents, conts):
        count = 0
        for c in conts:
            if c in sents:
                count += 1
        return count

    def get_word_id(self, token):
        """
        Return word id from ngram database.
        If word doesn't exist, then return -1.
        """
        try:
            return self.words.index(token.lower())
        except:
            return -1

    def get_sent_from_ids(self, sent):
        re_sent = []
        for i in sent:
            if i == 0 or i == self.words.index(tokenizer.END_TOKEN):
                continue
            re_sent.append(self.words[i])
        return re_sent

    def print_grams(self):
        for i in range(2, self.N):
            print(i, 'GRAM===========')
            for k in self.gram[i]:
                for j in range(len(k)):
                    print(self.words[j], end=',')
                print(':', self.gram[i][k])

    def sent_generate(self, out_sents, done_sents, till, count, contain):
        """
        contain = ['president', 'nepal']
        it returns list of sentences that is constructed using this ngram model
        start : starting word for sentence
        contain : list object which contains words that should be contained in
        constructed sentence.
        """

        if till not in done_sents:
            done_sents.append(till)
        n_words = self.get_next_word(till[:])
        # print('next words: ', [self.words[i[0]] for i in n_words])
        # print('till:', [self.words[i] for i in till])
        # print('## root_word', self.words[till[-1]])
        for w in n_words:
            # till_tmp = till_2[:]
            if w[0] == self.words.index(tokenizer.END_TOKEN) or \
               count > 10 or len(out_sents) > 500:
                # print('_END_TOKEN_')
                # print('till:', till)
                contain_count = self.get_count(till[:], contain)
                if contain_count > 0:
                    # print('sent_made :', [self.words[i] for i in till])
                    # if w is tokenizer.END_TOKEN:
                    if till[:] not in [x[0] for x in out_sents] and\
                       w[0] == self.words.index(tokenizer.END_TOKEN):
                        # print('sent:', self.get_sent_from_ids(
                            # till[:]), ' added -----------> !')
                        out_sents.append((till[:], contain_count))
                        print('sent:', self.get_sent_from_ids(
                            till[:]), 'count:', contain_count)
                        # return
                else:
                    continue
                    # print('no contain')
            else:
                # till_tmp.append(w[0])
                # print('till_tmp:', [self.words[i] for i in till_tmp])
                self.sent_generate(out_sents, done_sents,
                                   till[:] + [w[0]], count + 1, contain)
        else:
            pass
            # contain_count = self.get_count(till, contain)
            # out_sents.append((till, contain_count))
            # print("I don't know what you are talking about")
