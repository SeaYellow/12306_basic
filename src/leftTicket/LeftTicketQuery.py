import re
import requests
import json


class LeftTicketQuery:
    def queryStation(self):
        stationUrl = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8971"
        requests.packages.urllib3.disable_warnings()
        response = requests.get(stationUrl, verify=False)
        stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)', response.text)
        return dict(stations)

    def makeLeftTicketUrl(self, trainDate, fromStation, toStation, stations):
        fromStation = stations[fromStation]
        toStation = stations[toStation]
        print("fromStation : {} toStation : {}".format(fromStation, toStation))
        if fromStation == None or fromStation == "":
            return None
        if toStation == None or toStation == "":
            return None
        leftTicketUrl = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=" + trainDate + "&leftTicketDTO.from_station=" + fromStation + "&leftTicketDTO.to_station=" + toStation + "&purpose_codes=ADULT"
        print("leftTicketUrl : {}".format(leftTicketUrl))
        return leftTicketUrl

    def queryLeftTicket(self, leftTicketUrl, stationCodeName):
        requests.packages.urllib3.disable_warnings()
        response = requests.get(leftTicketUrl, verify=False)
        dictLeftTicket = json.loads(response.text)
        httpstatus = dictLeftTicket["httpstatus"]
        # 请求成功
        tickets = []
        if httpstatus == 200:
            data = dictLeftTicket["data"]
            result = data["result"]
            for line in result:
                cq = line.split("|")
                ticket = {}
                ticket["train_no"] = cq[2]  # 车票号
                ticket["station_train_code"] = cq[3]  # 车次
                ticket["start_station_telecode"] = cq[4]  # 起始站代号
                ticket["end_station_telecode"] = cq[5]  # 终点站代号
                ticket["from_station_telecode"] = cq[6]  # 出发站代号
                ticket["to_station_telecode"] = cq[7]  # 到达站代号
                ticket["start_time"] = cq[8]  # 出发时间
                ticket["arrive_time"] = cq[9]  # 到达时间
                ticket["lishi"] = cq[10]  # 历时
                ticket["canWebBuy"] = cq[11]  # 是否能购买：Y 可以
                ticket["yp_info"] = cq[12]
                ticket["start_train_date"] = cq[13]  # 出发日期
                ticket["train_seat_feature"] = cq[14]
                ticket["location_code"] = cq[15]
                ticket["from_station_no"] = cq[16]
                ticket["to_station_no"] = cq[17]
                ticket["is_support_card"] = cq[18]
                ticket["controlled_train_flag"] = cq[19]
                ticket["gg_num"] = cq[20]
                ticket["gr_num"] = cq[21]
                ticket["qt_num"] = cq[22]
                ticket["rw_num"] = cq[23]  # 软卧
                ticket["rz_num"] = cq[24]  # 软座
                ticket["tz_num"] = cq[25]
                ticket["wz_num"] = cq[26]  # 无座
                ticket["yb_num"] = cq[27]
                ticket["yw_num"] = cq[28]  # 硬卧
                ticket["yz_num"] = cq[29]
                ticket["ze_num"] = cq[30]  # 二等座
                ticket["zy_num"] = cq[31]  # 一等座
                ticket["swz_num"] = cq[32]  # 商务特等座
                ticket["srrb_num"] = cq[33]
                ticket["yp_ex"] = cq[34]
                ticket["seat_types"] = cq[35]
                ticket["exchange_train_flag"] = cq[36]
                ticket["from_station_name"] = stationCodeName[cq[6]]
                ticket["to_station_name"] = stationCodeName[cq[7]]
                tickets.append(ticket)
        else:
            print("Query left ticket wrong!")
        return tickets


if __name__ == '__main__':
    trainDate = "2018-05-21"
    fromStation = "西安"
    toStation = "成都"
    ltq = LeftTicketQuery()
    staticonNameCode = ltq.queryStation()
    stationCodeName = dict((v, k) for k, v in staticonNameCode.items())
    leftTicketUrl = ltq.makeLeftTicketUrl(trainDate, fromStation, toStation, staticonNameCode)
    if leftTicketUrl != None:
        tickets = ltq.queryLeftTicket(leftTicketUrl, stationCodeName)
        for ticket in tickets:
            ticketLine = "车次：" + ticket["station_train_code"] + " 出发日期：" + ticket["start_train_date"] + " 出发站：" + \
                         ticket["from_station_name"] + " 到达站：" + ticket["to_station_name"] + " 出发时间：" + ticket["start_time"] + " 到达时间：" + ticket[
                             "arrive_time"] + " 历时：" + ticket["lishi"] + " 商务座特等座：" + ticket["swz_num"] + " 一等座：" + ticket["zy_num"] + " 二等座：" + \
                         ticket["ze_num"] + " 高级软卧：" + ticket.get("yyrw_num", "") + " 软卧：" + ticket["rw_num"] + " 动卧：" + \
                         ticket["srrb_num"] + " 硬卧：" + ticket["yw_num"] + " 软座：" + ticket["rz_num"] + " 硬座：" + ticket["yz_num"] + " 无座：" + ticket["wz_num"]
            print(ticketLine)
    else:
        print("Query left ticket wrong!")
