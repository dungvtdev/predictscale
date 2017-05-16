def populate_params(self, **kwargs):
    self._endpoint = kwargs.get('endpoint')
    self._db_name = kwargs.get('db_name')
    self._batch_size = kwargs.get('batch_size', None)
    self._epoch = kwargs.get('epoch', None)
    self._metric = kwargs.get('metric', None)


class DataBatchGet():
    def get_data(self, begin, end, filter=None, **kwargs):
        # print('Get data from %s to %s' % (begin, end))

        _begin = end
        _end = end
        result = None
        batch_size = batch_size_by_time_dv(self.batch_size, self._epoch)
        count = 0

        def batch_data(result, begin, last):
            q = self.get_query(begin, last, **kwargs)
            rl = self.query_service.query_data(q)
            exdata = self.extract_data(rl)
            # print('%s %s %s' % (begin, last,
            #                     len(exdata) if exdata is not None else 0))
            if not exdata:
                return result, False, False
            finish = False
            if filter:
                fdata, finish = filter(exdata)
                result = self.extend_data(result, fdata)
            return result, finish, True

        while _begin > begin:
            _end = _begin
            _begin = _end - batch_size
            if _begin < begin:
                _begin = begin
            result, finish, has_more = batch_data(result, _begin, _end)
            if finish:
                break
            if not has_more:
                batch_size = batch_size * 2
                _begin = _end
            count = count + 1
        # print('Get Success %s' % count)
        return result

    def extend_data(self, current, new):
        if current is None:
            return new
        if new is not None:
            new.extend(current)
            del current
            return new
